import argparse
import os
import uuid
import json

import dpath.util
import re
import azureml.core
import base64
import zlib
from azureml.core import Dataset, Run, Datastore
from azureml.dataprep.api.errorhandlers import ExecutionError
from azureml.studio.core.error import UserError
from azureml.studio.core.io.data_frame_directory import DataFrameDirectory
from azureml.studio.core.data_frame_schema import DataFrameSchema
from azureml.studio.core.logger import logger, TimeProfile, time_profile
from azureml.studio.internal.error_handler import error_handler
from azureml.dataprep.api.dataflow import Dataflow
from msrest.exceptions import HttpOperationError, ClientRequestError
from pandas._libs.tslibs.np_datetime import OutOfBoundsDatetime
from urllib3.exceptions import ConnectTimeoutError

from azureml.designer.modules.dataio.common.decoretry import retry
from ..common.workspaceutil import get_workspace, get_time_as_string
from ..common.commonerrorutil import IMPORT_USER_ERROR_GROUP, get_error_group
from azureml.studio.internal.error import ErrorMapping, \
    CouldNotOpenFileError, CouldNotDownloadFileError, InvalidDatasetError, \
    IncorrectAzureMLDatastoreError, ParameterParsingError

logger.debug(f'Executing {os.path.abspath(__file__)}')
logger.debug(f"Azure ML SDK Version: {azureml.core.VERSION}")
logger.debug(f"DataPrep Version: {azureml.dataprep.__version__}")
logger.debug(
    f"azureml.designer.modules.dataio Version: {azureml.designer.modules.dataio.__version__}")


def ensure_dir(file_path):
    """Check if the directory exists"""
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def convert_to_lowercase(input_request_dto):
    """Convert capital letters in dictionary to lowercase"""
    new = {}
    for key, value in input_request_dto.items():
        if isinstance(value, dict):
            value = convert_to_lowercase(value)
        new_key = key[0].lower() + key[1:]
        new[new_key] = value
    return new


def check_url_format(url_str):
    """Check if input string is a url"""
    result = re.search('^(https?)://.*$', url_str)
    return True if result else False


def should_retry(ex):
    """Given an exception, judge whether to retry or fail immediately.

    :param: ex: the exception to judge.
    :return: True if need to retry, False otherwise.
    """
    if isinstance(ex, ConnectTimeoutError):
        return True
    if isinstance(ex, ExecutionError):
        code = getattr(ex, 'error_code', '')
        return code in ('ScriptExecution.StreamAccess.Throttling', 'ScriptExecution.StreamAccess.TimeoutExpired')
    return False


class ImportTabularDataModule:
    _HTTP_SOURCE = 'HttpSource'
    _HTTP_PATH_KEY = 'httpUrl'
    _AZURE_SQL_DATABASE_PATH_KEY = 'sqlDataPath/sqlQuery'
    _OTHERS_PATH_KEY = 'relativePath'

    @classmethod
    def __init__(cls, input_dict):
        cls.run_obj = Run.get_context()
        cls.workspace = get_workspace()
        cls.input_dataset_request_dto = input_dict['Input_dataset_request_DTO']
        cls.datastore_type = input_dict['Data_store_type']
        cls.override_datastore_name = input_dict['Override_data_store_name']
        cls.override_data_path = input_dict['Override_data_path']
        cls.dataset = None

    @staticmethod
    def get_datastore_type(workspace, datastore_name):
        """Check the data store type: http, sql, blob, adlgen1, adlgen2"""
        try:
            if datastore_name == '' or datastore_name is None:
                return ImportTabularDataModule._HTTP_SOURCE
            datastore = Datastore(workspace, datastore_name)
            return datastore.datastore_type
        except Exception as azureml_datastore_error:
            ErrorMapping.rethrow(
                azureml_datastore_error,
                IncorrectAzureMLDatastoreError(
                    datastore_name=datastore_name,
                    workspace_name=workspace))

    @staticmethod
    def get_path_key(store_type):
        """Get the key defined in requestDto"""
        if store_type in ['AzureSqlDatabase', 'AzurePostgreSql', 'AzureMySql']:
            path_key = ImportTabularDataModule._AZURE_SQL_DATABASE_PATH_KEY
        elif store_type in ['AzureFile']:
            path_key = ImportTabularDataModule._OTHERS_PATH_KEY
        elif store_type in ['HttpSource']:
            path_key = ImportTabularDataModule._HTTP_PATH_KEY
        else:
            path_key = ImportTabularDataModule._OTHERS_PATH_KEY
        return path_key

    @classmethod
    @time_profile
    def process_input_dataset_request_dto(cls, input_dataset_request_dto):
        """
        Process requestDto received from UI
        1. set name using run.tags.node_id
        2. register as hidden dataset
        3. for non-override scenario, keep source properties and set skip_validation=True. For override scenario,
           make source properties to be None and set skip_validation=False
        4. override datastore_name and data_path using override_datastore_name and override_data_path when available
        """
        try:
            # check if a json string or a compressed string
            if input_dataset_request_dto.startswith(
                    '{') and input_dataset_request_dto.endswith('}'):
                request = json.loads(input_dataset_request_dto)
            else:
                base64de = base64.b64decode(input_dataset_request_dto)
                decompressed_request_dto = zlib.decompress(
                    base64de).decode('utf-8')
                request = json.loads(decompressed_request_dto)

            request = convert_to_lowercase(request)

            # send http register request to service endpoint
            is_offline_run = cls.run_obj.id.startswith('OfflineRun')
            if not is_offline_run:
                # The customer has a scenario where to trigger a published import data pipeline endpoint using azure
                # function. The cpu type is compute cluster and node is 5.
                # Multiple jobs are registering datasets under the same name but with different paths. Each job
                # requests 1 node. It is caused by azureml.nodeid in tags sometimes has same value. Register method
                # in dataset service does not have handling for concurrent registration.
                # So we change the dataset name by using a new guid when registering a dataset in a pipeline job.
                if 'azureml.nodeid' in cls.run_obj.tags:
                    node_id = str(uuid.uuid4()) + '_' + cls.run_obj.tags.get('azureml.nodeid')
                else:
                    node_id = str(uuid.uuid4())
            else:
                node_id = str(uuid.uuid4())[:8]

            request['name'] = 'dataset_' + node_id
            request['isVisible'] = False

            if cls.override_data_path is None and cls.override_datastore_name is None:
                store_name = None
                if dpath.util.search(request, "dataPath/datastoreName"):
                    store_name = dpath.util.get(request, 'dataPath/datastoreName')
                store_type = ImportTabularDataModule.get_datastore_type(
                    cls.workspace, store_name)
                path_key = ImportTabularDataModule.get_path_key(store_type)
                try:
                    path = dpath.util.get(request['dataPath'], path_key)
                    if path is None or path == "":
                        raise Exception(f'The value of {path_key} is None.')
                except Exception:
                    ErrorMapping.throw(ParameterParsingError(arg_name_or_column=path_key))

                logger.info(
                    f"{get_time_as_string()} Process input request dto is done.")

                return request

            new_datapath = {}
            store_name = None
            if dpath.util.search(request, "dataPath/datastoreName"):
                store_name = dpath.util.get(request, 'dataPath/datastoreName')
            logger.info(f'DataStore Name: {store_name}')

            is_new_http_source = False
            if cls.override_data_path is not None and check_url_format(
                    cls.override_data_path):
                is_new_http_source = True

            if cls.override_datastore_name is not None and store_name != cls.override_datastore_name:
                store_name = cls.override_datastore_name

            store_type = ImportTabularDataModule.get_datastore_type(
                cls.workspace, store_name)
            path_key = ImportTabularDataModule.get_path_key(store_type)

            try:
                path = dpath.util.get(request['dataPath'], path_key)
            except Exception:
                ErrorMapping.throw(ParameterParsingError(arg_name_or_column=path_key))

            if cls.override_data_path is not None and path != cls.override_data_path:
                path = cls.override_data_path
                if is_new_http_source:
                    store_name = None
                    path_key = cls._HTTP_PATH_KEY

            dpath.util.new(new_datapath, 'datastoreName', store_name)
            dpath.util.new(new_datapath, path_key, path)

            request['dataPath'] = new_datapath
            if 'sourceProperties' in request:
                request['sourceProperties'] = None

            logger.info(
                f"{get_time_as_string()} Process input request dto is done.")
            logger.info(f"New request dto: {json.dumps(request)}")
            return request
        except Exception as err:
            raise err

    @classmethod
    @retry(tries=4, delay=90, backoff=1, logger=logger, should_retry=should_retry)
    def register_from_request(cls, request, skip_validate=False):
        dataset = Dataset._client()._register_from_request(cls.workspace,
                                                           dataset_request_dto=request,
                                                           as_pending=False,
                                                           exist_ok=True,
                                                           update_if_exists=True,
                                                           skip_validation=skip_validate)
        return dataset

    @classmethod
    @time_profile
    def generate_dataflow(cls) -> 'Dataflow':
        """Register requestDto to data set service endpoint"""
        logger.info('Start to register dto request.')
        request = cls.process_input_dataset_request_dto(cls.input_dataset_request_dto)

        try:
            if "sourceProperties" not in request:
                skip_validate = False
            else:
                skip_validate = False if request['sourceProperties'] is None else True

            try:
                cls.dataset = cls.register_from_request(request, skip_validate=skip_validate)
                logger.info(f"Return registered dataset: {repr(cls.dataset)}")
            except (ConnectTimeoutError, ClientRequestError) as conn_ex:
                ErrorMapping.rethrow(conn_ex, UserError('Connection time out. Please try later.'))

            data_definition = cls.dataset.get_definition()
            step_types = [s.step_type for s in data_definition._steps]
            logger.info(f'Dataflow for registered requestDto: {step_types}')
            for ss in data_definition._steps:
                logger.info(f'{repr(ss)}')
            logger.info(
                f"{get_time_as_string()} Register input request dto is done and registered dataset id: "
                f"{cls.dataset.id}")
            return data_definition
        except HttpOperationError as reg_exception:
            status_code = reg_exception.response.status_code
            error_message = str(reg_exception)
            hint_message = 'Status code: {0}. Register request failure. '.format(status_code) + \
                           error_message
            if status_code < 500:
                ErrorMapping.rethrow(reg_exception, UserError(hint_message))
            else:
                raise
        except Exception as exceptions:
            if isinstance(exceptions, ExecutionError):
                error_message = exceptions.compliant_message
            else:
                error_message = str(exceptions)

            if 'Requested file(s) does not exist or specified credential does not have access to read' in error_message:
                ErrorMapping.rethrow(
                    exceptions, CouldNotOpenFileError(file_name=request['dataPath']['relativePath']))
            elif 'The dataset type of the dataset is not Tabular' in error_message:
                ErrorMapping.rethrow(exceptions, CouldNotDownloadFileError(file_url=request['dataPath']['httpUrl']))
            else:
                raise exceptions

    @classmethod
    @retry(tries=4, delay=90, backoff=1, logger=logger, should_retry=should_retry)
    def to_pandas_dataframe(cls, data_flow, extended_type):
        df = Dataflow.to_pandas_dataframe(data_flow, extended_types=extended_type)
        return df

    @classmethod
    @error_handler
    @time_profile
    def run(cls, input_dict: dict = None) -> DataFrameDirectory:
        """Convert the dataset to pandas dataframe and create data frame directory object"""

        if 'Input_dataset_request_DTO' in input_dict:
            cls.input_dataset_request_dto = input_dict['Input_dataset_request_DTO']
        if 'Data_store_type' in input_dict:
            cls.datastore_type = input_dict['Data_store_type']
        if 'Override_data_store_name' in input_dict:
            cls.override_datastore_name = input_dict['Override_data_store_name']
        if 'Override_data_path' in input_dict:
            cls.override_data_path = input_dict['Override_data_path']

        try:
            data_flow = cls.generate_dataflow()
            if cls.datastore_type == 'AzureMySql':
                ErrorMapping.throw(UserError(f'AzureMySql datastore is not supported.'))

            logger.info(f'Start to create output port dfd')
            if data_flow is not None:
                try:
                    if cls.datastore_type in ['AzureSqlDatabase', 'AzurePostgreSql']:
                        data_frame = cls.to_pandas_dataframe(data_flow, extended_type=True)
                    else:
                        data_frame = cls.to_pandas_dataframe(data_flow, extended_type=False)
                except ConnectTimeoutError as conn_ex:
                    ErrorMapping.rethrow(conn_ex, UserError(f'Connection time out. Please try later.'))
                except OutOfBoundsDatetime as parquet_ex:
                    hint_message = "Value error when reading source data because data are invalid in Pandas " \
                                   "dataframe. " + str(parquet_ex)
                    ErrorMapping.rethrow(parquet_ex, UserError(hint_message))
                except OSError as os_ex:
                    if 'Cannot allocate memory' in str(os_ex):
                        ErrorMapping.rethrow(os_ex, UserError(str(os_ex)))
                    raise os_ex
                except Exception as pd_ex:
                    if 'RuntimeError: dataprep.native preppy error' in str(pd_ex):
                        ErrorMapping.rethrow(pd_ex, UserError(str(pd_ex)))
                    raise pd_ex

                if data_frame is None:
                    ErrorMapping.throw(InvalidDatasetError(dataset1=cls.dataset.id))
                schema = DataFrameSchema.data_frame_to_dict(data_frame)
        except Exception as import_exceptions:
            # Dataset/Dataprep Errors codes are combination of
            # 1. subset of dataprep errors, that map to "user errors"
            # 2. service codes (Reference: DatasetErrorCodes.cs)
            # 3. DataPrep python SDK
            error_code = getattr(import_exceptions, 'error_code', '')
            if isinstance(import_exceptions, ExecutionError):
                error_message = import_exceptions.compliant_message
            else:
                error_message = str(import_exceptions)

            if error_code in [
                'Validation', 'ScriptExecution.Validation', 'ScriptExecution.OutOfMemory', 'StepTranslation',
                'ScriptExecution.DatastoreResolution.NotFound', 'ScriptExecution.DatastoreResolution.Validation',
                'ScriptExecution.StreamAccess.NotFound', 'ScriptExecution.StreamAccess.Authentication',
                'ScriptExecution.StreamAccess.Authentication.Unexpected', 'ScriptExecution.StreamAccess',
                'ScriptExecution.DatabaseConnection', 'ScriptExecution.DatabaseConnection.NotFound',
                'ScriptExecution.DatabaseConnection.Authentication', 'ScriptExecution.DatabaseQuery',
                'ScriptExecution.DatabaseQuery.Timeout',  'ScriptExecution.DatabaseRead.Unexpected',
                'ScriptExecution.DatabaseRead', 'ScriptExecution.DatabaseQuery.Unexpected',
                'ScriptExecution.DatabaseRead.TimeoutExpired',
                'ScriptExecution.StreamAccess.Throttling', 'ScriptExecution.StreamAccess.TimeoutExpired',
                'ScriptExecution.StreamAccess.Validation', 'ScriptExecution.ReadDataFrame.StreamAccess.Validation',
                'ScriptExecution.Transformation.Validation', 'ScriptExecution.StreamAccess.Unexpected',
                'ScriptExecution.Unexpected.FieldConflict'
            ]:
                logger.debug(f'Error Code: {error_code}')
                ErrorMapping.rethrow(import_exceptions, UserError(error_message))

            if error_code == 'ScriptExecution.DatabaseQuery.TimeoutExpired':
                logger.debug(f'Error Code: {error_code}')
                hint_message = "Database query timeout. Please set Query timeout (seconds) in Import Data UI." \
                               + error_message
                ErrorMapping.rethrow(import_exceptions, UserError(hint_message))

            if 'Unexpected' in error_code:
                logger.debug(f'Error Code: {error_code}')
                ErrorMapping.rethrow(import_exceptions, UserError(error_message))

            if 'Authentication.AzureIdentityAccessTokenResolution' in error_code:
                logger.debug(f'Error Code: {error_code}')
                ErrorMapping.rethrow(import_exceptions, UserError(error_message))

            if any(m in error_message for m in IMPORT_USER_ERROR_GROUP):
                ErrorMapping.rethrow(import_exceptions, UserError(error_message))

            network_server_error_group = get_error_group(error_message)
            if network_server_error_group == 'ServerBusy' or network_server_error_group == 'connection issues' or \
                    network_server_error_group == 'gateway or load balancer error':
                hint_message = network_server_error_group + ' Please retry. ' + error_message
                ErrorMapping.rethrow(import_exceptions, UserError(hint_message))
            if network_server_error_group == 'memory allocation failures':
                hint_message = 'Out of memory, please try upgrade compute. ' + error_message
                ErrorMapping.rethrow(import_exceptions, UserError(hint_message))
            if network_server_error_group == 'access storage error':
                hint_message = 'Access azure storage failures. Please retry.' + error_message
                ErrorMapping.rethrow(import_exceptions, UserError(hint_message))
            raise import_exceptions

        output_port_dfd = DataFrameDirectory.create(
            data=data_frame, schema=schema, compute_visualization=True, compute_stats_in_visualization=True)
        logger.info(f"{get_time_as_string()} Create output port dtd is done")
        return output_port_dfd


@time_profile
def main(args):
    """
    Import data set from various data sources received from studio UI
    1.create input parameters dictionary
    2.initialize an import tabular data module
    3.register input dataset request dto to service endpoint and return a data frame directory
    4.save dataset as parquet and create schema/visualization sidecar files
    :param args:
    :return:
    """
    input_dataset_request_dto = args.input_dataset_request_dto
    datastore_type = args.datastore_type
    override_datastore_name = args.override_datastore_name
    override_data_path = args.override_data_path
    output_dir = args.output_dir

    logger.info(f'Received argument --datastore_type: {datastore_type}.')
    logger.info(
        f'Received argument --override_datastore_name: {override_datastore_name}.')

    input_dict = {
        'Input_dataset_request_DTO': input_dataset_request_dto,
        'Data_store_type': datastore_type,
        'Override_data_store_name': override_datastore_name,
        'Override_data_path': override_data_path,
    }

    import_tabular_data_module = ImportTabularDataModule(input_dict)

    data_frame_directory = import_tabular_data_module.run(input_dict)

    with TimeProfile('Save dataset and sidecar files'):
        ensure_dir(output_dir)
        data_frame_directory.dump(
            output_dir,
            overwrite_if_exist=True,
            validate_if_exist=True)

    logger.info(
        f"{get_time_as_string()} Save data set and sidecar files is done.")


def configs(parser):
    parser.add_argument(
        "--input_dataset_request_dto",
        type=str,
        help="Input dataset request Dto string")
    parser.add_argument("--datastore_type", type=str, help="Data store type")
    parser.add_argument(
        "--override_datastore_name",
        type=str,
        help="New data store name",
        default=None)
    parser.add_argument(
        "--override_data_path",
        type=str,
        help="New data path",
        default=None)
    parser.add_argument(
        "--output_dir",
        type=str,
        help="OutputPath for infer values from Output Ports")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    configs(parser)

    if os.environ.get('AML_PARAMETER_Override_data_store_name') == 'True':
        print("AML_PARAMETER_Override_data_store_name " +
              os.environ['AML_PARAMETER_Override_data_store_name'])
    else:
        print("There is no AML_PARAMETER_Override_data_store_name environment variable.")
    if os.environ.get('AML_PARAMETER_Override_data_path') == 'True':
        print("AML_PARAMETER_Override_data_path " +
              os.environ['AML_PARAMETER_Override_data_path'])
    else:
        print("There is no AML_PARAMETER_Override_data_path environment variable.")
    args, unknown = parser.parse_known_args()

    main(args)

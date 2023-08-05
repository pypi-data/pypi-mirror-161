import json

from azureml.core import Workspace, Run
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.studio.core.logger import logger
import time


def get_time_as_string():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())


def get_workspace_auth():
    with open('data/auth.json') as f:
        conf = json.load(f)

        if conf.get('service_principal_id') and conf.get('service_principal_password'):
            return ServicePrincipalAuthentication(
                tenant_id=conf.get('tenant_id'),
                service_principal_id=conf.get('service_principal_id'),
                service_principal_password=conf.get('service_principal_password'),
                cloud=conf.get('cloud_name'),
            )

        return None


def get_workspace():
    try:
        run = Run.get_context()
        if run.id.startswith('OfflineRun'):
            workspace = Workspace.from_config("data/config.json", auth=get_workspace_auth())
        else:
            workspace = run.experiment.workspace
        logger.info(f'Workspace information: {workspace}')
        return workspace
    except Exception as azureml_workspace_error:
        logger.error(
            f"{get_time_as_string()} Exception in get_workspace(): {str(azureml_workspace_error)}.")
        raise azureml_workspace_error

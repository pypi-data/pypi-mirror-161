"""
This file defines a subset of service errors that can be mapped to "user errors".
"""
# Reference runners_failure_analysis.py
ERROR_GROUPS = {
    'ServerBusy': [
        "ServerBusy",
        "The server is busy."
    ],
    'connection issues': [
        "Remote end closed connection without response",
        "Connection refused",
        "Connection timed out",
        "Connection reset by peer",
        "Temporary failure in name resolution",
        "ChunkedEncodingError: ('Connection broken: IncompleteRead(0 bytes read)', IncompleteRead(0 bytes read))",
        "Remote end closed connection without response",
        "bad handshake: SysCallError.-1, 'Unexpected EOF",
        "bad handshake: SysCallError.104, 'ECONNRESET",
        "requests.exceptions.ConnectionError: .'Connection aborted.', OSError",
        "bad handshake: SysCallError.110, 'ETIMEDOUT",
        'Failed to establish a new connection: .Errno -3. Temporary failure in name resolution',
        'Failed to establish a new connection: .Errno 110. Connection timed out',
        "Failed to establish a new connection: .Errno 111. Connection refused",
        "Unable to read data from the transport connection: Operation canceled.",
        "hostname 'cert-.*.experiments.azureml.net' doesn't match '.*.experiments.azureml.net'",
        "Name or service not known",
        "Connection reset by peer",
        "ChunkedEncodingError: ('Connection broken: IncompleteRead(0 bytes read'), IncompleteRead(0 bytes read))",
        "ChunkedEncodingError: ('Connection broken: OSError",
        "OSError: (104, 'ECONNRESET')",
        "urlopen error EOF occurred in violation of protocol",
        "he remote certificate is invalid according to the validation procedure"
    ],
    'memory allocation failures': [
        "Unable to allocate ",
        "for an array with shape",
        "and data type object"
    ],
    'gateway or load balancer error': [
        "Received 502 from a service request",
        "502 Server Error: Bad Gateway for url",
        "502 Bad Gateway",
        "504 Gateway Time-out",
        "too many 502 error responses",
        "msrest.exceptions.HttpOperationError: Operation returned an invalid status code 'Gateway Time-out'",
        "504 Server Error: Gateway",
        "status_code.: 504",
        "Bad Gateway",
        "Operation returned an invalid status code .Gateway Time-out",
        "502 Bad Gateway.",
        "The gateway did not receive a response from 'Microsoft.MachineLearningServices' within the specified time "
        "period.",
        "GatewayTimeout",
        "too many 504 error responses",
        "HTTPError: 530 Server Error"
    ],
    # Reference AzureStorage/AzureStorageConstants.cs
    'access storage error': [
        "The specified block list is invalid.",
        "The uncommitted block count cannot exceed the maximum limit",
        "The committed block count cannot exceed the maximum limit",
        "The block list may not contain more than",
        "The condition specified using HTTP conditional header(s) is not met.",
        "The specified container does not exist.",
        "Operations per second is over the account limit.",
        "Ingress is over the account limit.",
        "Egress is over the account limit.",
        "The specified account is disabled.",
        "The specified container is being deleted.",
        "The specified resource does not exist.",
        "The specified blob does not exist.",
        "The blob type is invalid for this operation.",
        "The specified blob already exists.",
        "The subscription associated with this vault has been disabled",
        "This request is not authorized to perform this operation"
    ],
}


EXPORT_USER_ERROR_GROUP = [
    "Access to Datastore denied with error response Forbidden",
    "Cannot create file",
    "Cannot create folder/filesystem",
    "Cannot create blob folder",
    "This request is not authorized to perform this operation using this permission",
    "Access to Datastore denied with error response Forbidden"
]


IMPORT_USER_ERROR_GROUP = [
    "Failed to create or update the dataset definition. The dataset definition has been created or update",
    "Object reference not set to an instance of an object",
    "Conversion failed when converting date and/or time from character string",
]


def get_error_group(err_msg):
    for error_group, error_messages in ERROR_GROUPS.items():
        if any(m in err_msg for m in error_messages):
            return error_group
    return None

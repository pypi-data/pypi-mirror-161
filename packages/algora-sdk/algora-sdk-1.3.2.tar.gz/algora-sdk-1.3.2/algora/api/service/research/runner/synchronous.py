from algora.api.service.research.runner.__util import _get_or_create_runner_request_info
from algora.common.decorators import data_request
from algora.common.requests import __put_request


@data_request(transformer=lambda data: data)
def get_or_create_runner() -> str:
    """
    Get or create runner.

    Returns:
        str: Runner ID
    """
    request_info = _get_or_create_runner_request_info()
    return __put_request(**request_info)

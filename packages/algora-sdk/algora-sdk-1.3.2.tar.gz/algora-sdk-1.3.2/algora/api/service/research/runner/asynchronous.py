from algora.api.service.research.runner.__util import _get_or_create_runner_request_info
from algora.common.decorators import async_data_request
from algora.common.requests import __async_put_request


@async_data_request(transformer=lambda data: data)
async def async_get_or_create_runner() -> str:
    """
    Asynchronously get or create runner.

    Returns:
        str: Runner ID
    """
    request_info = _get_or_create_runner_request_info()
    return await __async_put_request(**request_info)

from typing import Dict, Any

from algora.api.service.research.resource.__util import _get_resource_request_info, _delete_resource_request_info
from algora.common.decorators import async_data_request
from algora.common.function import no_transform
from algora.common.requests import __async_get_request, __async_delete_request


@async_data_request(transformer=lambda data: data, processor=lambda response: response.content)
async def async_get_resource(id: str) -> Dict[str, Any]:
    """
    Asynchronously get resource by ID.

    Args:
        id (str): Resource ID

    Returns:
        Dict[str, Any]: Resource response
    """
    request_info = _get_resource_request_info(id)
    return await __async_get_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_delete_resource(id: str) -> None:
    """
    Asynchronously delete resource by ID.

    Args:
        id (str): Resource ID

    Returns:
        None
    """
    request_info = _delete_resource_request_info(id)
    return await __async_delete_request(**request_info)

from typing import Dict, Any

from algora.api.service.research.resource.__util import _get_resource_request_info, _delete_resource_request_info
from algora.common.decorators import data_request
from algora.common.function import no_transform
from algora.common.requests import __get_request, __delete_request


@data_request(transformer=lambda data: data, processor=lambda response: response.content)
def get_resource(id: str) -> Dict[str, Any]:
    """
    Get resource by ID.

    Args:
        id (str): Resource ID

    Returns:
        Dict[str, Any]: Resource response
    """
    request_info = _get_resource_request_info(id)
    return __get_request(**request_info)


@data_request(transformer=no_transform)
def delete_resource(id: str) -> None:
    """
    Delete resource by ID.

    Args:
        id (str): Resource ID

    Returns:
        None
    """
    request_info = _delete_resource_request_info(id)
    return __delete_request(**request_info)

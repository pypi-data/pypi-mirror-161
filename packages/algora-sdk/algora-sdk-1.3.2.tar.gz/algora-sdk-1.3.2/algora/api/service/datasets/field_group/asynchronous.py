from typing import Dict, Any, List

from algora.api.service.datasets.field_group.__util import (
    _get_field_group_request_info, _get_field_groups_request_info, _create_field_group_request_info,
    _update_field_group_request_info, delete_field_group_request_info
)
from algora.api.service.datasets.field_group.model import FieldGroupRequest
from algora.common.decorators import async_data_request
from algora.common.function import no_transform
from algora.common.requests import (
    __async_get_request, __async_put_request, __async_post_request, __async_delete_request
)


@async_data_request(transformer=no_transform)
async def async_get_field_group(id: str) -> Dict[str, Any]:
    """
    Asynchronously get field group by ID.

    Args:
        id (str): Field group ID

    Returns:
        Dict[str, Any]: Field group response
    """
    request_info = _get_field_group_request_info(id)
    return await __async_get_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_get_field_groups() -> List[Dict[str, Any]]:
    """
    Asynchronously get all field groups.

    Returns:
        List[Dict[str, Any]]: List of field group response
    """
    request_info = _get_field_groups_request_info()
    return await __async_get_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_create_field_group(request: FieldGroupRequest) -> Dict[str, Any]:
    """
    Asynchronously create field group.

    Args:
        request (FieldGroupRequest): Field group request

    Returns:
        Dict[str, Any]: Field group response
    """
    request_info = _create_field_group_request_info(request)
    return await __async_put_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_update_field_group(id: str, request: FieldGroupRequest) -> Dict[str, Any]:
    """
    Asynchronously update field group.

    Args:
        id (str): Field group ID
        request (FieldGroupRequest): Field group request

    Returns:
        Dict[str, Any]: Field group response
    """
    request_info = _update_field_group_request_info(id, request)
    return await __async_post_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_delete_field_group(id: str) -> None:
    """
    Asynchronously delete field group by ID.

    Args:
        id (str): Field group ID

    Returns:
        None
    """
    request_info = delete_field_group_request_info(id)
    return await __async_delete_request(**request_info)

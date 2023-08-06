"""
Permission API requests.
"""
from typing import Dict, Any, List

from algora.api.service.permission.__util import (
    _get_permission_request_info, _delete_permission_request_info, _update_permission_request_info,
    _create_permission_request_info, _get_permissions_by_resource_id_request_info,
    _get_permission_by_resource_id_request_info
)
from algora.api.service.permission.model import PermissionRequest
from algora.common.decorators.data import async_data_request
from algora.common.function import no_transform
from algora.common.requests import (
    __async_get_request, __async_delete_request, __async_post_request, __async_put_request
)


@async_data_request(transformer=no_transform)
async def async_get_permission(id: str) -> Dict[str, Any]:
    """
    Asynchronously get permission by ID.

    Args:
        id (str): Permission ID

    Returns:
        Dict[str, Any]: Permission response
    """
    request_info = _get_permission_request_info(id)
    return await __async_get_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_get_permission_by_resource_id(resource_id: str) -> Dict[str, Any]:
    """
    Asynchronously get permission by resource ID.

    Args:
        resource_id (str): Resource ID

    Returns:
        Dict[str, Any]: Permission response
    """
    request_info = _get_permission_by_resource_id_request_info(resource_id)
    return await __async_get_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_get_permissions_by_resource_id(resource_id: str) -> List[Dict[str, Any]]:
    """
    Asynchronously get all permissions by resource ID.

    Args:
        resource_id (str): Resource ID

    Returns:
        List[Dict[str, Any]]: List of permission response
    """
    request_info = _get_permissions_by_resource_id_request_info(resource_id)
    return await __async_get_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_create_permission(request: PermissionRequest) -> Dict[str, Any]:
    """
    Asynchronously create permission.

    Args:
        request (PermissionRequest): Permission request

    Returns:
        Dict[str, Any]: Permission response
    """
    request_info = _create_permission_request_info(request)
    return await __async_put_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_update_permission(id: str, request: PermissionRequest) -> Dict[str, Any]:
    """
    Asynchronously update permission.

    Args:
        id: (str): Permission ID
        request (PermissionRequest): Permission request

    Returns:
        Dict[str, Any]: Permission response
    """
    request_info = _update_permission_request_info(id, request)
    return await __async_post_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_delete_permission(id: str) -> None:
    """
    Asynchronously delete permission by ID.

    Args:
        id: (str): Permission ID

    Returns:
        None
    """
    request_info = _delete_permission_request_info(id)
    return await __async_delete_request(**request_info)

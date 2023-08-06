from typing import Dict, Any, List

from algora.api.service.permission.__util import (
    _get_permission_request_info, _delete_permission_request_info, _update_permission_request_info,
    _create_permission_request_info, _get_permissions_by_resource_id_request_info,
    _get_permission_by_resource_id_request_info
)
from algora.api.service.permission.model import PermissionRequest
from algora.common.decorators import data_request
from algora.common.function import no_transform
from algora.common.requests import __get_request, __delete_request, __post_request, __put_request


@data_request(transformer=no_transform)
def get_permission(id: str) -> Dict[str, Any]:
    """
    Get permission by ID.

    Args:
        id (str): Permission ID

    Returns:
        Dict[str, Any]: Permission response
    """
    request_info = _get_permission_request_info(id)
    return __get_request(**request_info)


@data_request(transformer=no_transform)
def get_permission_by_resource_id(resource_id: str) -> Dict[str, Any]:
    """
    Get permission by resource ID.

    Args:
        resource_id (str): Resource ID

    Returns:
        Dict[str, Any]: Permission response
    """
    request_info = _get_permission_by_resource_id_request_info(resource_id)
    return __get_request(**request_info)


@data_request(transformer=no_transform)
def get_permissions_by_resource_id(resource_id: str) -> List[Dict[str, Any]]:
    """
    Get all permissions by resource ID.

    Args:
        resource_id (str): Resource ID

    Returns:
        List[Dict[str, Any]]: List of permission response
    """
    request_info = _get_permissions_by_resource_id_request_info(resource_id)
    return __get_request(**request_info)


@data_request(transformer=no_transform)
def create_permission(request: PermissionRequest) -> Dict[str, Any]:
    """
    Create permission.

    Args:
        request (PermissionRequest): Permission request

    Returns:
        Dict[str, Any]: Permission response
    """
    request_info = _create_permission_request_info(request)
    return __put_request(**request_info)


@data_request(transformer=no_transform)
def update_permission(id: str, request: PermissionRequest) -> Dict[str, Any]:
    """
    Update permission.

    Args:
        id: (str): Permission ID
        request (PermissionRequest): Permission request

    Returns:
        Dict[str, Any]: Permission response
    """
    request_info = _update_permission_request_info(id, request)
    return __post_request(**request_info)


@data_request(transformer=no_transform)
def delete_permission(id: str) -> None:
    """
    Delete permission by ID.

    Args:
        id: (str): Permission ID

    Returns:
        None
    """
    request_info = _delete_permission_request_info(id)
    return __delete_request(**request_info)

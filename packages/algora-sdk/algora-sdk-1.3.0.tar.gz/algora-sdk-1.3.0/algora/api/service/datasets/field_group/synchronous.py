from typing import Dict, Any, List

from algora.api.service.datasets.field_group.__util import (
    _get_field_group_request_info, _get_field_groups_request_info, _create_field_group_request_info,
    _update_field_group_request_info, delete_field_group_request_info
)
from algora.api.service.datasets.field_group.model import FieldGroupRequest
from algora.common.decorators import data_request
from algora.common.function import no_transform
from algora.common.requests import __get_request, __put_request, __post_request, __delete_request


@data_request(transformer=no_transform)
def get_field_group(id: str) -> Dict[str, Any]:
    """
    Get field group by ID.

    Args:
        id (str): Field group ID

    Returns:
        Dict[str, Any]: Field group response
    """
    request_info = _get_field_group_request_info(id)
    return __get_request(**request_info)


@data_request(transformer=no_transform)
def get_field_groups() -> List[Dict[str, Any]]:
    """
    Get all field groups.

    Returns:
        List[Dict[str, Any]]: List of field group response
    """
    request_info = _get_field_groups_request_info()
    return __get_request(**request_info)


@data_request(transformer=no_transform)
def create_field_group(request: FieldGroupRequest) -> Dict[str, Any]:
    """
    Create field group.

    Args:
        request (FieldGroupRequest): Field group request

    Returns:
        Dict[str, Any]: Field group response
    """
    request_info = _create_field_group_request_info(request)
    return __put_request(**request_info)


@data_request(transformer=no_transform)
def update_field_group(id: str, request: FieldGroupRequest) -> Dict[str, Any]:
    """
    Update field group.

    Args:
        id (str): Field group ID
        request (FieldGroupRequest): Field group request

    Returns:
        Dict[str, Any]: Field group response
    """
    request_info = _update_field_group_request_info(id, request)
    return __post_request(**request_info)


@data_request(transformer=no_transform)
def delete_field_group(id: str) -> None:
    """
    Delete field group by ID.

    Args:
        id (str): Field group ID

    Returns:
        None
    """
    request_info = delete_field_group_request_info(id)
    return __delete_request(**request_info)

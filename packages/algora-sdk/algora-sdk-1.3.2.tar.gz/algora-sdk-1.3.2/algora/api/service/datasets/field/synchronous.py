from typing import Dict, Any

from algora.api.service.datasets.field.__util import (
    _delete_field_request_info, _create_field_request_info, _get_field_request_info, _update_field_request_info
)
from algora.api.service.datasets.field.model import FieldRequest
from algora.common.decorators import data_request
from algora.common.function import no_transform
from algora.common.requests import __delete_request, __post_request, __put_request, __get_request


@data_request(transformer=no_transform)
def get_field(id: str) -> Dict[str, Any]:
    """
    Get field by ID.

    Args:
        id (str): Field ID

    Returns:
        Dict[str, Any]: Field response
    """
    request_info = _get_field_request_info(id)
    return __get_request(**request_info)


@data_request(transformer=no_transform)
def create_field(request: FieldRequest) -> Dict[str, Any]:
    """
    Create field.

    Args:
        request (FieldRequest): Field request

    Returns:
        Dict[str, Any]: Field response
    """
    request_info = _create_field_request_info(request)
    return __put_request(**request_info)


@data_request(transformer=no_transform)
def update_field(id: str, request: FieldRequest) -> Dict[str, Any]:
    """
    Update field.

    Args:
        id (str): Field ID
        request (FieldRequest): Field request

    Returns:
        Dict[str, Any]: Field response
    """
    request_info = _update_field_request_info(id, request)
    return __post_request(**request_info)


@data_request(transformer=no_transform)
def delete_field(id: str) -> None:
    """
    Delete field by ID.

    Args:
        id (str): Field ID

    Returns:
        None
    """
    request_info = _delete_field_request_info(id, )
    return __delete_request(**request_info)

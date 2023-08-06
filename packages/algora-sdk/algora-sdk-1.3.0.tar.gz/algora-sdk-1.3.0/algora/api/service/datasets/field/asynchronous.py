from typing import Dict, Any

from algora.api.service.datasets.field.__util import (
    _delete_field_request_info, _create_field_request_info, _get_field_request_info, _update_field_request_info
)
from algora.api.service.datasets.field.model import FieldRequest
from algora.common.decorators import async_data_request
from algora.common.function import no_transform
from algora.common.requests import (
    __async_delete_request, __async_post_request, __async_put_request, __async_get_request
)


@async_data_request(transformer=no_transform)
async def async_get_field(id: str) -> Dict[str, Any]:
    """
    Asynchronously get field by ID.

    Args:
        id (str): Field ID

    Returns:
        Dict[str, Any]: Field response
    """
    request_info = _get_field_request_info(id)
    return await __async_get_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_create_field(request: FieldRequest) -> Dict[str, Any]:
    """
    Asynchronously create field.

    Args:
        request (FieldRequest): Field request

    Returns:
        Dict[str, Any]: Field response
    """
    request_info = _create_field_request_info(request)
    return await __async_put_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_update_field(id: str, request: FieldRequest) -> Dict[str, Any]:
    """
    Asynchronously update field.

    Args:
        id (str): Field ID
        request (FieldRequest): Field request

    Returns:
        Dict[str, Any]: Field response
    """
    request_info = _update_field_request_info(id, request)
    return await __async_post_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_delete_field(id: str) -> None:
    """
    Asynchronously delete field by ID.

    Args:
        id (str): Field ID

    Returns:
        None
    """
    request_info = _delete_field_request_info(id, )
    return await __async_delete_request(**request_info)

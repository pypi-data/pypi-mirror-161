from typing import List, Dict, Any

from algora.api.service.datasets.field.model import FieldRequest
from algora.api.service.datasets.schema.__util import (
    _delete_schema_request_info, _update_schema_fields_request_info, _update_schema_request_info,
    _create_schema_request_info, _get_schema_fields_request_info, _get_schemas_request_info, _get_schema_request_info
)
from algora.api.service.datasets.schema.model import SchemaRequest
from algora.common.decorators import async_data_request
from algora.common.function import no_transform
from algora.common.requests import (
    __async_get_request, __async_post_request, __async_put_request, __async_delete_request
)


@async_data_request(transformer=no_transform)
async def async_get_schema(id: str) -> Dict[str, Any]:
    """
    Asynchronously get schema by ID.

    Args:
        id (str): Schema ID

    Returns:
        Dict[str, Any]: Schema response
    """
    request_info = _get_schema_request_info(id)
    return await __async_get_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_get_schemas() -> List[Dict[str, Any]]:
    """
    Asynchronously get all schemas.

    Returns:
        List[Dict[str, Any]]: List of schema response
    """
    request_info = _get_schemas_request_info()
    return await __async_get_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_get_schema_fields(id: str) -> List[Dict[str, Any]]:
    """
    Asynchronously get schema fields.

    Args:
        id (str): Schema ID

    Returns:
        List[Dict[str, Any]]: List of field response
    """
    request_info = _get_schema_fields_request_info(id)
    return await __async_get_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_create_schema(request: SchemaRequest) -> Dict[str, Any]:
    """
    Asynchronously create schema.

    Args:
        request (SchemaRequest): Schema request

    Returns:
        Dict[str, Any]: Schema response
    """
    request_info = _create_schema_request_info(request)
    return await __async_put_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_update_schema(id: str, request: SchemaRequest) -> Dict[str, Any]:
    """
    Asynchronously update schema.

    Args:
        id (str): Schema ID
        request (SchemaRequest): Schema request

    Returns:
        Dict[str, Any]: Schema response
    """
    request_info = _update_schema_request_info(id, request)
    return await __async_post_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_update_schema_fields(id: str, request: List[FieldRequest]) -> List[Dict[str, Any]]:
    """
    Asynchronously update schema fields.

    Args:
        id (str): Schema ID
        request (List[FieldRequest]): List of field request

    Returns:
         List[Dict[str, Any]]: List of field response
    """
    request_info = _update_schema_fields_request_info(id, request)
    return await __async_post_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_delete_schema(id: str) -> None:
    """
    Asynchronously delete schema by ID.

    Args:
        id (str): Schema ID

    Returns:
        None
    """
    request_info = _delete_schema_request_info(id)
    return await __async_delete_request(**request_info)

from typing import List, Dict, Any

from algora.api.service.datasets.field.model import FieldRequest
from algora.api.service.datasets.schema.__util import (
    _delete_schema_request_info, _update_schema_fields_request_info, _update_schema_request_info,
    _create_schema_request_info, _get_schema_fields_request_info, _get_schemas_request_info, _get_schema_request_info
)
from algora.api.service.datasets.schema.model import SchemaRequest
from algora.common.decorators import data_request
from algora.common.function import no_transform
from algora.common.requests import __delete_request, __post_request, __put_request, __get_request


@data_request(transformer=no_transform)
def get_schema(id: str) -> Dict[str, Any]:
    """
    Get schema by ID.

    Args:
        id (str): Schema ID

    Returns:
        Dict[str, Any]: Schema response
    """
    request_info = _get_schema_request_info(id)
    return __get_request(**request_info)


@data_request(transformer=no_transform)
def get_schemas() -> List[Dict[str, Any]]:
    """
    Get all schemas.

    Returns:
        List[Dict[str, Any]]: List of schema response
    """
    request_info = _get_schemas_request_info()
    return __get_request(**request_info)


@data_request(transformer=no_transform)
def get_schema_fields(id: str) -> List[Dict[str, Any]]:
    """
    Get schema fields.

    Args:
        id (str): Schema ID

    Returns:
        List[Dict[str, Any]]: List of field response
    """
    request_info = _get_schema_fields_request_info(id)
    return __get_request(**request_info)


@data_request(transformer=no_transform)
def create_schema(request: SchemaRequest) -> Dict[str, Any]:
    """
    Create schema.

    Args:
        request (SchemaRequest): Schema request

    Returns:
        Dict[str, Any]: Schema response
    """
    request_info = _create_schema_request_info(request)
    return __put_request(**request_info)


@data_request(transformer=no_transform)
def update_schema(id: str, request: SchemaRequest) -> Dict[str, Any]:
    """
    Update schema.

    Args:
        id (str): Schema ID
        request (SchemaRequest): Schema request

    Returns:
        Dict[str, Any]: Schema response
    """
    request_info = _update_schema_request_info(id, request)
    return __post_request(**request_info)


@data_request(transformer=no_transform)
def update_schema_fields(id: str, request: List[FieldRequest]) -> List[Dict[str, Any]]:
    """
    Update schema fields.

    Args:
        id (str): Schema ID
        request (List[FieldRequest]): List of field request

    Returns:
         List[Dict[str, Any]]: List of field response
    """
    request_info = _update_schema_fields_request_info(id, request)
    return __post_request(**request_info)


@data_request(transformer=no_transform)
def delete_schema(id: str) -> None:
    """
    Delete schema by ID.

    Args:
        id (str): Schema ID

    Returns:
        None
    """
    request_info = _delete_schema_request_info(id)
    return __delete_request(**request_info)

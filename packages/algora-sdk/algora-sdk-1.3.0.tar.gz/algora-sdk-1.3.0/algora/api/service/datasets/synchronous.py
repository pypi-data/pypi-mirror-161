from typing import Dict, Any, List

from algora.api.service.datasets.__util import (
    _get_dataset_request_info, _get_datasets_request_info, _search_datasets_request_info, _create_dataset_request_info,
    _update_dataset_request_info, _delete_dataset_request_info
)
from algora.api.service.datasets.model import DatasetSearchRequest, DatasetRequest
from algora.common.decorators import data_request
from algora.common.function import no_transform
from algora.common.requests import __get_request, __post_request, __put_request, __delete_request


@data_request(transformer=no_transform)
def get_dataset(id: str) -> Dict[str, Any]:
    """
    Get dataset by ID.

    Args:
        id (str): Dataset ID

    Returns:
        Dict[str, Any]: Dataset response
    """
    request_info = _get_dataset_request_info(id)
    return __get_request(**request_info)


@data_request(transformer=no_transform)
def get_datasets() -> List[Dict[str, Any]]:
    """
    Get all datasets.

    Returns:
        List[Dict[str, Any]]: List of dataset response
    """
    request_info = _get_datasets_request_info()
    return __get_request(**request_info)


@data_request(transformer=no_transform)
def search_datasets(request: DatasetSearchRequest) -> List[Dict[str, Any]]:
    """
    Search all datasets.

    Args:
        request (DatasetSearchRequest): Dataset search request

    Returns:
        List[Dict[str, Any]]: List of dataset response
    """
    request_info = _search_datasets_request_info(request)
    return __post_request(**request_info)


@data_request(transformer=no_transform)
def create_dataset(request: DatasetRequest) -> Dict[str, Any]:
    """
    Create dataset.

    Args:
        request (DatasetRequest): Dataset request

    Returns:
        Dict[str, Any]: Dataset response
    """
    request_info = _create_dataset_request_info(request)
    return __put_request(**request_info)


@data_request(transformer=no_transform)
def update_dataset(id: str, request: DatasetRequest) -> Dict[str, Any]:
    """
    Update dataset.

    Args:
        id (str): Dataset ID
        request (DatasetRequest): Dataset request

    Returns:
        Dict[str, Any]: Dataset response
    """
    request_info = _update_dataset_request_info(id, request)
    return __post_request(**request_info)


@data_request(transformer=no_transform)
def delete_dataset(id: str) -> None:
    """
    Delete dataset by ID.

    Args:
        id (str): Dataset ID

    Returns:
        None
    """
    request_info = _delete_dataset_request_info(id)
    return __delete_request(**request_info)

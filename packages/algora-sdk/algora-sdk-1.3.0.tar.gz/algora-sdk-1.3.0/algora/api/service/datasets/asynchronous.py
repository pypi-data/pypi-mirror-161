from typing import Dict, Any, List

from algora.api.service.datasets.__util import (
    _get_dataset_request_info, _get_datasets_request_info, _search_datasets_request_info, _create_dataset_request_info,
    _update_dataset_request_info, _delete_dataset_request_info
)
from algora.api.service.datasets.model import DatasetSearchRequest, DatasetRequest
from algora.common.decorators import async_data_request
from algora.common.function import no_transform
from algora.common.requests import (
    __async_get_request, __async_post_request, __async_put_request, __async_delete_request
)


@async_data_request(transformer=no_transform)
async def async_get_dataset(id: str) -> Dict[str, Any]:
    """
    Asynchronously get dataset by ID.

    Args:
        id (str): Dataset ID

    Returns:
        Dict[str, Any]: Dataset response
    """
    request_info = _get_dataset_request_info(id)
    return await __async_get_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_get_datasets() -> List[Dict[str, Any]]:
    """
    Asynchronously get all datasets.

    Returns:
        List[Dict[str, Any]]: List of dataset response
    """
    request_info = _get_datasets_request_info()
    return await __async_get_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_search_datasets(request: DatasetSearchRequest) -> List[Dict[str, Any]]:
    """
    Asynchronously search all datasets.

    Args:
        request (DatasetSearchRequest): Dataset search request

    Returns:
        List[Dict[str, Any]]: List of dataset response
    """
    request_info = _search_datasets_request_info(request)
    return await __async_post_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_create_dataset(request: DatasetRequest) -> Dict[str, Any]:
    """
    Asynchronously create dataset.

    Args:
        request (DatasetRequest): Dataset request

    Returns:
        Dict[str, Any]: Dataset response
    """
    request_info = _create_dataset_request_info(request)
    return await __async_put_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_update_dataset(id: str, request: DatasetRequest) -> Dict[str, Any]:
    """
    Asynchronously update dataset.

    Args:
        id (str): Dataset ID
        request (DatasetRequest): Dataset request

    Returns:
        Dict[str, Any]: Dataset response
    """
    request_info = _update_dataset_request_info(id, request)
    return await __async_post_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_delete_dataset(id: str) -> None:
    """
    Asynchronously delete dataset by ID.

    Args:
        id (str): Dataset ID

    Returns:
        None
    """
    request_info = _delete_dataset_request_info(id)
    return await __async_delete_request(**request_info)

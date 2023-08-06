from requests import Response

from algora.api.data.query.__util import _query_datasets_request_info, _query_dataset_csv_request_info
from algora.common.requests import __async_post_request, __async_get_request


async def async_query_dataset(id: str, data=None, json=None) -> Response:
    """
    Asynchronously query dataset by ID.

    Args:
        id (str): Dataset ID
        data (Any): Data to POST
        json (Any): Data to POST

    Returns:
        Response: HTTP response object
    """
    request_info = _query_datasets_request_info(id, data, json)
    return await __async_post_request(**request_info)


async def async_query_dataset_csv(id: str, data=None) -> Response:
    """
    Asynchronously query dataset CSV by ID.

    Args:
        id (str): Dataset ID
        data (Any): Data to POST

    Returns:
        Response: HTTP response object
    """
    request_info = _query_dataset_csv_request_info(id, data)
    return await __async_get_request(**request_info)

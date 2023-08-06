from typing import List, Any, Dict

from algora.api.service.document.__util import (
    _get_document_request_info, _search_documents_request_info, _create_document_request_info,
    _update_document_request_info, _delete_document_request_info
)
from algora.api.service.document.model import SearchDocumentRequest, DocumentRequest
from algora.common.decorators import async_data_request
from algora.common.function import no_transform
from algora.common.requests import (
    __async_get_request, __async_put_request, __async_post_request, __async_delete_request,
)


@async_data_request(transformer=no_transform)
async def async_get_document(id: str) -> Dict[str, Any]:
    """
    Asynchronously get document by ID.

    Args:
        id: (str): Document ID

    Returns:
        Dict[str, Any]: Document response
    """
    request_info = _get_document_request_info(id)
    return await __async_get_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_search_documents(request: SearchDocumentRequest) -> List[Dict[str, Any]]:
    """
    Asynchronously search all documents.

    Args:
        request: (SearchDocumentRequest): Document search request

    Returns:
        List[Dict[str, Any]]: List of document response
    """
    request_info = _search_documents_request_info(request)
    return await __async_post_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_create_document(request: DocumentRequest) -> Dict[str, Any]:
    """
    Asynchronously create document.

    Args:
        request: (DocumentRequest): Document request

    Returns:
        Dict[str, Any]: Document response
    """
    request_info = _create_document_request_info(request)
    return await __async_post_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_update_document(id: str, request: DocumentRequest) -> Dict[str, Any]:
    """
    Asynchronously update document.

    Args:
        id (str): Document ID
        request: (DocumentRequest): Document request

    Returns:
        Dict[str, Any]: Document response
    """
    request_info = _update_document_request_info(id, request)
    return await __async_put_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_delete_document(id: str) -> None:
    """
    Asynchronously delete document by ID.

    Args:
        id (str): Document ID

    Returns:
        None
    """
    request_info = _delete_document_request_info(id)
    return await __async_delete_request(**request_info)

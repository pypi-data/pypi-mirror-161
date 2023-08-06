from typing import Dict, Any, List

from algora.api.service.document.__util import (
    _get_document_request_info, _search_documents_request_info, _create_document_request_info,
    _update_document_request_info, _delete_document_request_info
)
from algora.api.service.document.model import SearchDocumentRequest, DocumentRequest
from algora.common.decorators import data_request
from algora.common.function import no_transform
from algora.common.requests import (
    __get_request, __put_request, __post_request, __delete_request,
)


@data_request(transformer=no_transform)
def get_document(id: str) -> Dict[str, Any]:
    """
    Get document by ID.

    Args:
        id: (str): Document ID

    Returns:
        Dict[str, Any]: Document response
    """
    request_info = _get_document_request_info(id)
    return __get_request(**request_info)


@data_request(transformer=no_transform)
def search_documents(request: SearchDocumentRequest) -> List[Dict[str, Any]]:
    """
    Search all documents.

    Args:
        request: (SearchDocumentRequest): Document search request

    Returns:
        List[Dict[str, Any]]: List of document response
    """
    request_info = _search_documents_request_info(request)
    return __post_request(**request_info)


@data_request(transformer=no_transform)
def create_document(request: DocumentRequest) -> Dict[str, Any]:
    """
    Create document.

    Args:
        request: (DocumentRequest): Document request

    Returns:
        Dict[str, Any]: Document response
    """
    request_info = _create_document_request_info(request)
    return __post_request(**request_info)


@data_request(transformer=no_transform)
def update_document(id: str, request: DocumentRequest) -> Dict[str, Any]:
    """
    Update document.

    Args:
        id (str): Document ID
        request: (DocumentRequest): Document request

    Returns:
        Dict[str, Any]: Document response
    """
    request_info = _update_document_request_info(id, request)
    return __put_request(**request_info)


@data_request(transformer=no_transform)
def delete_document(id: str) -> None:
    """
    Delete document by ID.

    Args:
        id (str): Document ID

    Returns:
        None
    """
    request_info = _delete_document_request_info(id)
    return __delete_request(**request_info)

from typing import Dict, Any

from algora.api.service.research.__util import _get_research_request_info
from algora.common.decorators.data import data_request
from algora.common.requests import __get_request


@data_request(transformer=lambda data: data)
def get_research(id: str) -> Dict[str, Any]:
    """
    Get research by ID.

    Args:
        id (str): Research ID

    Returns:
        Dict[str, Any]: Research response
    """
    request_info = _get_research_request_info(id)
    return __get_request(**request_info)

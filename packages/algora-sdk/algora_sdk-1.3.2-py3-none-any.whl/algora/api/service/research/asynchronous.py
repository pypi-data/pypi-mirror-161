from typing import Dict, Any

from algora.api.service.research.__util import _get_research_request_info
from algora.common.decorators.data import async_data_request
from algora.common.requests import __async_get_request


@async_data_request(transformer=lambda data: data)
async def async_get_research(id: str) -> Dict[str, Any]:
    """
    Asynchronously get research by ID.

    Args:
        id (str): Research ID

    Returns:
        Dict[str, Any]: Research response
    """
    request_info = _get_research_request_info(id)
    return await __async_get_request(**request_info)

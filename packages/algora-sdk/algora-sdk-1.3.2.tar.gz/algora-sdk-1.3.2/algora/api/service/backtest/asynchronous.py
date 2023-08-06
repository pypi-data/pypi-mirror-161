"""
Backtest API requests.
"""
from typing import Dict, Any, List

from algora.api.service.backtest.__util import (
    _get_backtest_request_info, _get_backtests_request_info, _create_backtest_request_info,
    _update_backtest_request_info, _delete_backtest_request_info
)
from algora.api.service.backtest.model import BacktestRequest, BacktestStatus
from algora.common.decorators import async_data_request
from algora.common.function import no_transform
from algora.common.requests import (
    __async_get_request, __async_put_request, __async_post_request, __async_delete_request
)


@async_data_request(transformer=no_transform)
async def async_get_backtest(id: str) -> Dict[str, Any]:
    """
    Asynchronously get backtest by ID.

    Args:
        id (str): Backtest ID

    Returns:
        Dict[str, Any]: Backtest response
    """
    request_info = _get_backtest_request_info(id)
    return await __async_get_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_get_backtests() -> List[Dict[str, Any]]:
    """
    Asynchronously get all backtests.

    Returns:
        List[Dict[str, Any]]: List of backtest response
    """
    request_info = _get_backtests_request_info()
    return await __async_get_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_create_backtest(request: BacktestRequest) -> Dict[str, Any]:
    """
    Asynchronously create backtest.

    Args:
        request (BacktestRequest): Backtest request

    Returns:
        Dict[str, Any]: Backtest response
    """
    request_info = _create_backtest_request_info(request)
    return await __async_put_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_update_backtest(id: str, status: BacktestStatus) -> Dict[str, Any]:
    """
    Asynchronously update backtest.

    Args:
        id (str): Backtest ID
        status (BacktestRequest): Backtest request

    Returns:
        Dict[str, Any]: Backtest response
    """
    request_info = _update_backtest_request_info(id, status)
    return await __async_post_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_delete_backtest(id: str) -> None:
    """
    Asynchronously delete backtest by ID.

    Args:
        id (str): Backtest ID

    Returns:
        None
    """
    request_info = _delete_backtest_request_info(id, )
    return await __async_delete_request(**request_info)

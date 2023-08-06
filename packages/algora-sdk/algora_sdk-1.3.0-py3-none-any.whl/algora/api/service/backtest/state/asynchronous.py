from typing import Dict, Any

import pandas as pd

from algora.api.service.backtest.state.__util import (
    _get_all_portfolio_state_request_info, _get_all_cash_payments_request_info, _create_portfolio_state_request_info,
    _create_cash_payment_request_info
)
from algora.api.service.backtest.state.model import PortfolioStateRequest, CashPaymentRequest
from algora.common.decorators import async_data_request
from algora.common.enum import Order
from algora.common.function import no_transform
from algora.common.requests import __async_put_request, __async_get_request


@async_data_request
async def async_get_all_portfolio_state(backtest_id: str, order: Order = Order.ASC, **kwargs) -> pd.DataFrame:
    """
    Asynchronously get all portfolio states.

    Args:
        backtest_id (str): Backtest ID
        order (Order): SQL Order
        **kwargs: Extra arguments

    Returns:
        DataFrame: DataFrame of portfolio states
    """
    request_info = _get_all_portfolio_state_request_info(backtest_id, order, **kwargs)
    return await __async_get_request(**request_info)


@async_data_request
async def async_get_all_cash_payments(backtest_id: str, order: Order = Order.ASC, **kwargs) -> pd.DataFrame:
    """
    Asynchronously get all cash payments.

    Args:
        backtest_id (str): Backtest ID
        order (Order): SQL Order
        **kwargs: Extra arguments

    Returns:
        DataFrame: DataFrame of cash payments
    """
    request_info = _get_all_cash_payments_request_info(backtest_id, order, **kwargs)
    return await __async_get_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_create_portfolio_state(request: PortfolioStateRequest) -> Dict[str, Any]:
    """
    Asynchronously create portfolio state.

    Args:
        request (PortfolioStateRequest): Portfolio state request

    Returns:
        Dict[str, Any]: Portfolio state response
    """
    request_info = _create_portfolio_state_request_info(request)
    return await __async_put_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_create_cash_payment(request: CashPaymentRequest) -> Dict[str, Any]:
    """
    Asynchronously create cash payment.

    Args:
        request (CashPaymentRequest): Cash payment request

    Returns:
        Dict[str, Any]: Cash payment response
    """
    request_info = _create_cash_payment_request_info(request)
    return await __async_put_request(**request_info)

from typing import Dict, Any

import pandas as pd

from algora.api.service.backtest.state.__util import (
    _get_all_portfolio_state_request_info, _get_all_cash_payments_request_info, _create_portfolio_state_request_info,
    _create_cash_payment_request_info
)
from algora.api.service.backtest.state.model import CashPaymentRequest, PortfolioStateRequest
from algora.common.decorators import data_request
from algora.common.enum import Order
from algora.common.function import no_transform
from algora.common.requests import __put_request, __get_request


@data_request
def get_all_portfolio_state(backtest_id: str, order: Order = Order.ASC, **kwargs) -> pd.DataFrame:
    """
    Get all portfolio states.

    Args:
        backtest_id (str): Backtest ID
        order (Order): SQL Order
        **kwargs: Extra arguments

    Returns:
        DataFrame: DataFrame of portfolio states
    """
    request_info = _get_all_portfolio_state_request_info(backtest_id, order, **kwargs)
    return __get_request(**request_info)


@data_request
def get_all_cash_payments(backtest_id: str, order: Order = Order.ASC, **kwargs) -> pd.DataFrame:
    """
    Get all cash payments.

    Args:
        backtest_id (str): Backtest ID
        order (Order): SQL Order
        **kwargs: Extra arguments

    Returns:
        DataFrame: DataFrame of cash payments
    """
    request_info = _get_all_cash_payments_request_info(backtest_id, order, **kwargs)
    return __get_request(**request_info)


@data_request(transformer=no_transform)
def create_portfolio_state(request: PortfolioStateRequest) -> Dict[str, Any]:
    """
    Create portfolio state.

    Args:
        request (PortfolioStateRequest): Portfolio state request

    Returns:
        Dict[str, Any]: Portfolio state response
    """
    request_info = _create_portfolio_state_request_info(request)
    return __put_request(**request_info)


@data_request(transformer=no_transform)
def create_cash_payment(request: CashPaymentRequest) -> Dict[str, Any]:
    """
    Create cash payment.

    Args:
        request (CashPaymentRequest): Cash payment request

    Returns:
        Dict[str, Any]: Cash payment response
    """
    request_info = _create_cash_payment_request_info(request)
    return __put_request(**request_info)

import json

from algora.api.service.backtest.state.model import PortfolioStateRequest, CashPaymentRequest
from algora.common.enum import Order


def _get_all_portfolio_state_request_info(backtest_id: str, order: Order = Order.ASC, **kwargs) -> dict:
    config = {
        "endpoint": f"config/backtest/{backtest_id}/state/portfolio?order={order}"
    }
    kwargs.update(config)

    return kwargs


def _get_all_cash_payments_request_info(backtest_id: str, order: Order, **kwargs) -> dict:
    config = {
        "endpoint": f"config/backtest/{backtest_id}/state/cash_payment?order={order}"
    }
    kwargs.update(config)

    return kwargs


def _create_portfolio_state_request_info(request: PortfolioStateRequest) -> dict:
    return {
        "endpoint": "config/backtest/state/portfolio",
        "json": json.loads(request.json())
    }


def _create_cash_payment_request_info(request: CashPaymentRequest) -> dict:
    return {
        "endpoint": "config/backtest/state/cash_payment",
        "json": json.loads(request.json())
    }

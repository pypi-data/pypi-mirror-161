import json

from algora.api.service.backtest.enum import BacktestStatus
from algora.api.service.backtest.model import BacktestRequest


def _get_backtest_request_info(id: str) -> dict:
    return {
        "endpoint": f"config/backtest/{id}"
    }


def _get_backtests_request_info() -> dict:
    return {
        "endpoint": f"config/backtest"
    }


def _create_backtest_request_info(request: BacktestRequest) -> dict:
    return {
        "endpoint": "config/backtest",
        "json": json.loads(request.json())
    }


def _update_backtest_request_info(id: str, status: BacktestStatus):
    return {
        "endpoint": f"config/backtest/{id}",
        "json": status.value
    }


def _delete_backtest_request_info(id: str):
    return {
        "endpoint": f"config/backtest/{id}",
    }

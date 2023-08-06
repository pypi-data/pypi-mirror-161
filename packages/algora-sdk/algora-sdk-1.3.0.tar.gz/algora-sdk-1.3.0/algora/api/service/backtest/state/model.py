from datetime import date
from typing import Optional

from algora.api.service.backtest.state.enum import BacktestEventType
from algora.common.base import Base


class BacktestEvent(Base):
    backtest_id: str
    backtest_type: BacktestEventType


class CashPaymentRequest(Base):
    backtest_id: str
    payment_date: date
    type: str
    amount: float
    position_id: Optional[str]
    currency: Optional[str]


class PortfolioStateRequest(Base):
    backtest_id: str
    date: date
    valuation: float
    pnl: float
    portfolio: str


class CashPaymentResponse(BacktestEvent):
    id: str
    backtest_id: str
    backtest_type: BacktestEventType
    payment_date: date
    type: str
    amount: float
    position_id: Optional[str]
    currency: Optional[str]
    created_at: int


class PortfolioStateResponse(BacktestEvent):
    id: str
    backtest_id: str
    backtest_type: BacktestEventType
    date: date
    valuation: float
    pnl: float
    portfolio: str
    created_at: int


class BacktestMetricRequest(Base):
    backtest_id: str
    metrics: str

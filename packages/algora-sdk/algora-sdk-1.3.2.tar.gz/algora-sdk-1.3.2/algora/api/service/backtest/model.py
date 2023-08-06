from datetime import date
from typing import Optional

from algora.api.service.backtest.enum import BacktestType, BacktestStatus
from algora.common.base import Base


class BacktestRequest(Base):
    strategy_id: str
    type: BacktestType
    status: BacktestStatus
    start_date: date
    end_date: date
    portfolio: str  # TODO replace with portfolio object in Quant SDK


class BacktestResponse(Base):
    id: str
    strategy_id: str
    type: BacktestType
    status: BacktestStatus
    start_date: date
    end_date: date
    portfolio: str  # TODO replace with portfolio object in Quant SDK
    created_by: str
    created_at: int
    updated_by: Optional[str]
    updated_at: Optional[int]


class BacktestViewResponse(Base):
    id: str
    strategy_id: str
    strategy_name: str
    type: BacktestType
    status: BacktestStatus
    start_date: date
    end_date: date
    portfolio: str  # TODO replace with portfolio object in Quant SDK
    created_by: str
    created_at: int
    updated_by: Optional[str]
    updated_at: Optional[int]

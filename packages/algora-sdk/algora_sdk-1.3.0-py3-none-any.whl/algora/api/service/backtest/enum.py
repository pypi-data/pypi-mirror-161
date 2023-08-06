from algora.common.base import BaseEnum


class BacktestType(BaseEnum):
    STRATEGY = 'STRATEGY'
    BACKTEST = 'BACKTEST'


class BacktestStatus(BaseEnum):
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    CANCELED = 'CANCELED'

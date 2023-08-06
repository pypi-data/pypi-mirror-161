from algora.common.base import BaseEnum


class AssetClass(BaseEnum):
    COMMODITY = "commodity"
    CREDIT = "credit"
    EQUITY = "equity"
    FOREX = "forex"
    RATES = "rates"


class Repository(BaseEnum):
    CME = "CME"
    DTCC = "DTCC"
    ICE = "ICE"

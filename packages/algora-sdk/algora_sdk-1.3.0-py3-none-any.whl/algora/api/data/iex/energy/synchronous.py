from pandas import DataFrame

from algora.api.data.iex.__utils import __base_request
from algora.api.data.iex.energy.__util import __build_params
from algora.common.decorators import data_request


@data_request
def historical_oil_prices(symbol: str, **kwargs) -> DataFrame:
    """
    Wrapper for IEX's Historical Energy Prices via Time Series API

    Reference: https://iexcloud.io/docs/api/#time-series-endpoint

    Args:
        symbol (str): "DCOILWTICO" or "DCOILBRENTEU"
        **kwargs: Optional args to pass to the IEX API

    Returns:
        DataFrame: Historical oil prices for the provided symbol
    """
    params = __build_params(**kwargs)
    return __base_request(f"time-series/energy/{symbol}", **params)

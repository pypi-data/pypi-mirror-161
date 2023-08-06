from pandas import DataFrame

from algora.api.data.iex.__utils import __async_base_request
from algora.api.data.iex.energy.__util import __build_params
from algora.common.decorators.data import async_data_request


@async_data_request
async def async_historical_oil_prices(symbol: str, **kwargs) -> DataFrame:
    """
    Async wrapper for IEX's Historical Energy Prices via Time Series API

    Reference: https://iexcloud.io/docs/api/#time-series-endpoint

    Args:
        symbol (str): "DCOILWTICO" or "DCOILBRENTEU"
        **kwargs: Optional args to pass to the IEX API

    Returns:
        DataFrame: Historical oil prices for the provided symbol
    """
    # default query params
    params = __build_params(**kwargs)
    return await __async_base_request(f"time-series/energy/{symbol}", **params)

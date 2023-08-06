from typing import Union, Dict, List

from pandas import DataFrame

from algora.api.data.iex.__utils import __async_base_request
from algora.api.data.iex.stocks.__util import (
    _symbols_request_info, _historical_prices_request_info, _news_request_info, _peer_group_request_info
)
from algora.common.decorators import async_data_request
from algora.common.function import transform_one_or_many, no_transform


@async_data_request
async def async_symbols() -> DataFrame:
    """
    Asynchronous wrapper for IEX's API to get symbols that IEX Cloud supports for intraday price updates.

    Reference: https://iexcloud.io/docs/api/#symbols

    Returns:
        DataFrame: IEX supported symbols
    """
    request_info = _symbols_request_info()
    return await __async_base_request(**request_info)


@async_data_request(transformer=lambda d: transform_one_or_many(d, 'chart'))
async def async_historical_prices(*symbol: str, **kwargs) -> Union[DataFrame, Dict[str, DataFrame]]:
    """
    Asynchronous wrapper for IEX's Historical Prices via Time Series API

    Reference: https://iexcloud.io/docs/api/#time-series-endpoint

    Args:
         symbol (*str): Stock symbol(s), such as "AAPL" or "AAPL", "FB"
         **kwargs: Optional args to pass to the IEX API

    Returns:
        Union[DataFrame, Dict[str, DataFrame]]: Historical prices for the symbol(s) requested
    """
    # default query params
    request_info = _historical_prices_request_info(*symbol, **kwargs)
    return await __async_base_request(**request_info)


@async_data_request
async def async_news(symbol: str, **kwargs) -> DataFrame:
    """
    Asynchronous wrapper for IEX's API to get news for given symbol
    Reference: https://iexcloud.io/docs/api/#news

    Args:
        symbol (str): Stock symbol, such as AAPL
        **kwargs: Optional args to pass to the IEX API

    Returns:
        DataFrame: News for the symbol requested
    """
    request_info = _news_request_info(symbol, kwargs)
    return await __async_base_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_peer_group(symbol: str) -> List[str]:
    """
    Asynchronous wrapper for IEX's API to get stock peers

    Reference: https://iexcloud.io/docs/api/#peers

    Args:
        symbol (str): Stock symbol, such as AAPL

    Returns:
         List[str]: List of symbols
    """
    request_info = _peer_group_request_info(symbol)
    return await __async_base_request(**request_info)

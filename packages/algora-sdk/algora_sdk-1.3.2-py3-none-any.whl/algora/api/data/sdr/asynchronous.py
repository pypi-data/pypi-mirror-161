from typing import Optional, List

from pandas import DataFrame

from algora.api.data.query import async_query_dataset
from algora.api.data.sdr.__util import (
    _get_by_date_request_info, _get_distinct_in_field_request_info, _commodity_request_info, _credit_request_info,
    _rates_request_info, _forex_request_info, _equity_request_info
)
from algora.api.data.sdr.enum import AssetClass, Repository
from algora.api.data.sdr.model import DataFilter
from algora.common.decorators import async_data_request
from algora.common.function import to_pandas_with_index, no_transform
from algora.common.requests import __async_get_request


@async_data_request(transformer=lambda data: to_pandas_with_index(data, index='execution_timestamp'))
async def async_get_by_date(asset_class: AssetClass, date: str, repos: Optional[List[Repository]] = None) -> DataFrame:
    """
    Asynchronously get all SDR data by asset class, date and repositories.

    Args:
        asset_class (AssetClass): Asset class enum (COMMODITY, CREDIT, EQUITY, FOREX, RATES)
        date (str): Date in YYYY-MM-DD format (e.g. "2022-01-01")
        repos (Optional[List[Repository]]): Repository enum list (e.g. [CME, DTCC, ICE])

    Returns:
        DataFrame: DataFrame
    """
    request_info = _get_by_date_request_info(asset_class, date, repos)
    return await __async_get_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_get_distinct_in_field(asset_class: AssetClass, field: str) -> List[str]:
    """
    Asynchronously get all distinct values in field.

    Args:
        asset_class (AssetClass): Asset class enum (COMMODITY, CREDIT, EQUITY, FOREX, RATES)
        field (str): Field to query for

    Returns:
        List[str]: List of all distinct values in field
    """
    request_info = _get_distinct_in_field_request_info(asset_class, field)
    return await __async_get_request(**request_info)


@async_data_request
async def async_commodity(filter: Optional[DataFilter] = None):
    """
    Asynchronously get SDR Commodity dataset.

    Args:
        filter (Optional[DataFilter]): Dataset query filter

    Returns:
        DataFrame: DataFrame
    """
    request_info = _commodity_request_info(filter)
    return await async_query_dataset(**request_info)


@async_data_request
async def async_credit(filter: Optional[DataFilter] = None):
    """
    Asynchronously get SDR Credit dataset.

    Args:
        filter (Optional[DataFilter]): Dataset query filter

    Returns:
        DataFrame: DataFrame
    """
    request_info = _credit_request_info(filter)
    return await async_query_dataset(**request_info)


@async_data_request
async def async_equity(filter: Optional[DataFilter] = None):
    """
    Asynchronously get SDR Equity dataset.

    Args:
        filter (Optional[DataFilter]): Dataset query filter

    Returns:
        DataFrame: DataFrame
    """
    request_info = _equity_request_info(filter)
    return await async_query_dataset(**request_info)


@async_data_request
async def async_forex(filter: Optional[DataFilter] = None):
    """
    Asynchronously get SDR Forex dataset.

    Args:
        filter (Optional[DataFilter]): Dataset query filter

    Returns:
        DataFrame: DataFrame
    """
    request_info = _forex_request_info(filter)
    return await async_query_dataset(**request_info)


@async_data_request
async def async_rates(filter: Optional[DataFilter] = None):
    """
    Asynchronously get SDR Rates dataset.

    Args:
        filter (Optional[DataFilter]): Dataset query filter

    Returns:
        DataFrame: DataFrame
    """
    request_info = _rates_request_info(filter)
    return await async_query_dataset(**request_info)

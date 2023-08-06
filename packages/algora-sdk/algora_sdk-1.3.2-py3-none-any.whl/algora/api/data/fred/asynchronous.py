from pandas import DataFrame

from algora.api.data.fred.__util import _transform_fred_observations, _get_series_info
from algora.api.data.fred.model import FredQuery
from algora.common.decorators import async_data_request
from algora.common.requests import __async_get_request


@async_data_request(transformer=_transform_fred_observations)
async def async_get_series(query: FredQuery):
    """
    Asynchronously get FRED series.

    Args:
        query (FredQuery): FRED query

    Returns:
        DataFrame: DataFrame
    """
    request_info = _get_series_info(query)
    return await __async_get_request(**request_info)

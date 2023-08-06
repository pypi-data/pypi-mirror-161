from pandas import DataFrame

from algora.api.data.fred.__util import _transform_fred_observations, _get_series_info
from algora.api.data.fred.model import FredQuery
from algora.common.decorators import data_request
from algora.common.requests import __get_request


@data_request(transformer=_transform_fred_observations)
def get_series(query: FredQuery) -> DataFrame:
    """
    Get FRED series.

    Args:
        query (FredQuery): FRED query

    Returns:
        DataFrame: DataFrame
    """
    request_info = _get_series_info(query)
    return __get_request(**request_info)

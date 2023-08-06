from typing import Dict, Any

import pandas as pd
from pandas import DataFrame

from algora.api.data.fred.model import FredQuery


def _transform_fred_observations(data: Dict[str, Any]) -> DataFrame:
    return pd.DataFrame(data['observations'])


def _get_series_info(query: FredQuery) -> dict:
    return {
        "endpoint": "/series/observations",
        "url_key": "fred",
        "params": query.dict(exclude_none=True)
    }

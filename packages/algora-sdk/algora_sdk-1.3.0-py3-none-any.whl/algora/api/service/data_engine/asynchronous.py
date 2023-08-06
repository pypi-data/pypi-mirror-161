import io
from typing import Dict, Any, Optional

import pandas as pd
from pandas import DataFrame

from algora.api.service.data_engine.__util import _analyze_data_request_info, _transform_data_request_info
from algora.api.service.data_engine.model import TransformOverride
from algora.common.decorators.data import async_data_request
from algora.common.function import no_transform
from algora.common.requests import __async_post_request


@async_data_request(transformer=no_transform)
async def async_analyze_data(data: pd.DataFrame) -> Dict[str, Any]:
    request_info = _analyze_data_request_info(data)
    return await __async_post_request(**request_info)


@async_data_request(processor=lambda r: r.content, transformer=lambda r: pd.read_parquet(io.BytesIO(r)))
async def async_transform_data(data: pd.DataFrame, transform_override: Optional[TransformOverride] = None) -> DataFrame:
    request_info = _transform_data_request_info(data, transform_override)
    return await __async_post_request(**request_info)

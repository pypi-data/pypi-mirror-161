from typing import Optional

import pandas as pd

from algora.api.service.data_engine.model import TransformOverride


def _analyze_data_request_info(data: pd.DataFrame) -> dict:
    parquet_bytes = data.to_parquet()

    return {
        'endpoint': "data-engine/alpha/analyze",
        'files': {'file': parquet_bytes}
    }


def _transform_data_request_info(data: pd.DataFrame, transform_override: Optional[TransformOverride] = None) -> dict:
    if transform_override is not None:
        transform_override = {'transform_override': transform_override.json()}
    else:
        transform_override = None

    parquet_bytes = data.to_parquet()

    return {
        'endpoint': f"data-engine/alpha/transform",
        'data': transform_override,
        'files': {'file': parquet_bytes}
    }

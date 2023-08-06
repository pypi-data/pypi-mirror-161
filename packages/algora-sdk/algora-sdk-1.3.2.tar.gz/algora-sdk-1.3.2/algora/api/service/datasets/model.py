from typing import Optional, List

from algora.api.service.datasets.enum import DatasetDataType
from algora.common.base import Base


class DatasetRequest(Base):
    display_name: str
    logical_name: str
    description: Optional[str]
    data_type: DatasetDataType
    data_query: str
    data_query_type: str
    schema_id: str
    directory_id: str


class DatasetSearchRequest(Base):
    query: str
    data_types: Optional[List[str]]  # TODO make enum

from typing import Optional, Union, List

from algora.api.service.data_engine.enum import FieldFill
from algora.common.base import Base
from algora.common.enum import FieldType


class FieldMetric(Base):
    name: str
    type: FieldType
    length: int
    num_null: int
    num_zero: int
    min: Optional[Union[float, int]]
    max: Optional[Union[float, int]]
    std_dev: Optional[float]


class FieldOverride(Base):
    name: str
    type: Optional[FieldType] = None
    fill: Optional[FieldFill] = None


class TransformOverride(Base):
    fields: List[FieldOverride] = []
    default_fill: FieldFill = FieldFill.PREVIOUS

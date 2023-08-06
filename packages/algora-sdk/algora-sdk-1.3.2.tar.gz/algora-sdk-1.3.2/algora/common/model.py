from algora.common.base import Base
from algora.common.enum import FieldType
from algora.common.type import Datetime


class Field(Base):
    logical_name: str
    type: FieldType


class DataRequest(Base):
    """
    Base data request, inherited by all instrument-specific data request classes.
    """
    date: Datetime

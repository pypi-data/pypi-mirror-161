from typing import List, Optional, Union

from algora.common.base import Base


class LogicalDisplayName(Base):
    display_name: str
    logical_name: str


class DateRange(Base):
    start_date: str
    end_date: str
    enabled: bool


class APIFieldFilter(Base):
    logical_display: LogicalDisplayName
    operator: str  # operator can be "NOT_IN" or "IN" or "NOT_EQUAL" or "EQUAL" or "GTE" or "GT" or "LTE" or "LT"
    selected_values: List[str]


class FieldFilter(Base):
    field: str
    operator: str  # operator can be "NOT_IN" or "IN" or "NOT_EQUAL" or "EQUAL" or "GTE" or "GT" or "LTE" or "LT"
    selected_values: List[str]


class DataFilter(Base):
    date_range: Optional[DateRange]
    filters: List[Union[FieldFilter, APIFieldFilter]]

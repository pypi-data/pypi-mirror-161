"""
Common types.
"""
from datetime import date
from typing import NewType, Union, List, Dict

from pandas import DataFrame

Datetime = NewType('Datetime', date)  # TODO add in datetime
DataResponse = NewType('DataResponse', Union[DataFrame, List[DataFrame], Dict[str, DataFrame], float])
PriceResult = NewType('PriceResult', Union[float])
RiskResult = NewType('RiskResult', Union[float])

from typing import Optional

from pydantic import Field, validator

from algora.common.base import Base
from algora.common.type import Datetime


class FredQuery(Base):
    api_key: str
    series_id: str
    file_type: str = Field(default='json')
    observation_start: Optional[Datetime] = None
    observation_end: Optional[Datetime] = None

    # necessary for proper .dict() serialization
    @validator("observation_start")
    def observation_start_to_string(cls, d):
        return d.isoformat()

    @validator("observation_end")
    def observation_end_to_string(cls, d):
        return d.isoformat()

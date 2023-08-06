from typing import Optional, List

from algora.common.base import Base
from algora.common.enum import FieldType


class FieldRequest(Base):
    display_name: str
    logical_name: str
    type: FieldType
    width: int
    editable: bool
    hidden: bool
    display_order: int
    tags: List[str]  # TODO make enum
    schema_id: str
    field_group_id: Optional[str]

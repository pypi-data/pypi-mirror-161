from typing import Optional, Dict, Union, Any

from algora.common.base import Base


class DocumentRequest(Base):
    name: str
    type: str
    classification: str
    document: Union[str, Dict]


class SearchDocumentRequest(Base):
    name: Optional[str]
    type: Optional[str]
    classification: Optional[str]
    is_released: Optional[bool]


class Document(Base):
    pk: str
    parent_pk: str
    original_pk: str
    name: str
    type: str
    classification: str
    document: Union[str, Dict[str, Any]]
    created_by: str
    created_at: int
    updated_by: str
    updated_at: int
    released_by: str
    released_at: int
    is_released: bool
    deleted_by: str
    deleted_at: int
    is_deleted: bool

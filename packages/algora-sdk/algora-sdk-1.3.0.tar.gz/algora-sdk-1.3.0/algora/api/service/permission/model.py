from algora.api.service.permission.enum import PermissionType
from algora.common.base import Base


class PermissionRequest(Base):
    resource_id: str
    permission_type: PermissionType
    permission_id: str
    view: bool
    edit: bool
    delete: bool
    edit_permission: bool

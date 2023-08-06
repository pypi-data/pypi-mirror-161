import json

from algora.api.service.permission.model import PermissionRequest


def _get_permission_request_info(id: str) -> dict:
    return {
        'endpoint': f"config/permission/{id}"
    }


def _get_permission_by_resource_id_request_info(resource_id: str) -> dict:
    return {
        'endpoint': f"config/permission/resource/{resource_id}"
    }


def _get_permissions_by_resource_id_request_info(resource_id: str) -> dict:
    return {
        'endpoint': f"config/permission/resource/{resource_id}/permissions"
    }


def _create_permission_request_info(request: PermissionRequest) -> dict:
    return {
        'endpoint': f"config/permission",
        'json': json.loads(request.json())
    }


def _update_permission_request_info(id: str, request: PermissionRequest) -> dict:
    return {
        'endpoint': f"config/permission/{id}",
        'json': json.loads(request.json())
    }


def _delete_permission_request_info(id: str) -> dict:
    return {
        'endpoint': f"config/permission/{id}"
    }

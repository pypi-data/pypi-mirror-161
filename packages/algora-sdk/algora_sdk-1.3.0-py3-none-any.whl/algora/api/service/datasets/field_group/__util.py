import json

from algora.api.service.datasets.field_group.model import FieldGroupRequest


def _get_field_group_request_info(id: str) -> dict:
    return {
        "endpoint": f"config/datasets/field-group/{id}"
    }


def _get_field_groups_request_info() -> dict:
    return {
        "endpoint": f"config/datasets/field-group"
    }


def _create_field_group_request_info(request: FieldGroupRequest) -> dict:
    return {
        "endpoint": f"config/datasets/field-group",
        "json": json.loads(request.json())
    }


def _update_field_group_request_info(id: str, request: FieldGroupRequest) -> dict:
    return {
        "endpoint": f"config/datasets/field-group/{id}",
        "json": json.loads(request.json())
    }


def delete_field_group_request_info(id: str) -> dict:
    return {
        "endpoint": f"config/datasets/field-group/{id}"
    }

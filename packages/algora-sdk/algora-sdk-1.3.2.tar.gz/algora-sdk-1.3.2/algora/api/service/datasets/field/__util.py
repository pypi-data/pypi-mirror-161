import json

from algora.api.service.datasets.field.model import FieldRequest


def _get_field_request_info(id: str) -> dict:
    return {
        "endpoint": f"config/datasets/field/{id}"
    }


def _create_field_request_info(request: FieldRequest) -> dict:
    return {
        "endpoint": "config/datasets/field",
        "json": json.loads(request.json())
    }


def _update_field_request_info(id: str, request: FieldRequest):
    return {
        "endpoint": f"config/datasets/field/{id}",
        "json": json.loads(request.json())
    }


def _delete_field_request_info(id: str):
    return {
        "endpoint": f"config/datasets/field/{id}",
    }

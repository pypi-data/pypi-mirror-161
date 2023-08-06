import json
from typing import List

from algora.api.service.datasets.field.model import FieldRequest
from algora.api.service.datasets.schema.model import SchemaRequest


def _get_schema_request_info(id: str) -> dict:
    return {
        "endpoint": f"config/datasets/schema/{id}"
    }


def _get_schemas_request_info() -> dict:
    return {
        "endpoint": f"config/datasets/schema"
    }


def _get_schema_fields_request_info(id: str) -> dict:
    return {
        "endpoint": f"config/datasets/schema/{id}/fields"
    }


def _create_schema_request_info(request: SchemaRequest) -> dict:
    return {
        "endpoint": f"config/datasets/schema",
        "json": json.loads(request.json())
    }


def _update_schema_request_info(id: str, request: SchemaRequest) -> dict:
    return {
        "endpoint": f"config/datasets/schema/{id}",
        "json": json.loads(request.json())
    }


def _update_schema_fields_request_info(id: str, request: List[FieldRequest]) -> dict:
    return {
        "endpoint": f"config/datasets/schema/{id}/fields",
        "json": [json.loads(f.json()) for f in request]
    }


def _delete_schema_request_info(id: str) -> dict:
    return {
        "endpoint": f"config/datasets/schema/{id}"
    }

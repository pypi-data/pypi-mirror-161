import json

from algora.api.service.datasets.model import DatasetSearchRequest, DatasetRequest


def _get_dataset_request_info(id: str) -> dict:
    return {
        "endpoint": f"config/datasets/dataset/{id}"
    }


def _get_datasets_request_info() -> dict:
    return {
        "endpoint": f"config/datasets/dataset"
    }


def _search_datasets_request_info(request: DatasetSearchRequest) -> dict:
    return {
        "endpoint": f"config/datasets/dataset/search",
        "json": json.loads(request.json())
    }


def _create_dataset_request_info(request: DatasetRequest) -> dict:
    return {
        "endpoint": f"config/datasets/dataset",
        "json": json.loads(request.json())
    }


def _update_dataset_request_info(id: str, request: DatasetRequest) -> dict:
    return {
        "endpoint": f"config/datasets/dataset/{id}",
        "json": json.loads(request.json())
    }


def _delete_dataset_request_info(id: str) -> dict:
    return {
        "endpoint": f"config/datasets/dataset/{id}"
    }

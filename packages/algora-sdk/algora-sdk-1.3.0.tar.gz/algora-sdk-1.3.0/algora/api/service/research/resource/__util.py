def _get_resource_request_info(id: str) -> dict:
    return {
        'endpoint': f"config/resource/{id}/resource"
    }


def _delete_resource_request_info(id: str):
    return {
        'endpoint': f"config/resource/{id}"
    }

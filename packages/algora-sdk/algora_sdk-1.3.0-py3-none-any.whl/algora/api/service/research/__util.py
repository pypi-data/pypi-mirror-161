def _get_research_request_info(id: str) -> dict:
    return {
        'endpoint': f"config/research/research/{id}"
    }

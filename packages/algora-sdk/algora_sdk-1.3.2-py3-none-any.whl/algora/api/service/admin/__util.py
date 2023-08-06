from typing import List, Dict


def _get_client_id_request_info() -> dict:
    return {
        "endpoint": "clients?clientId=realm-management",
        "url_key": "keycloak"
    }


def _get_users_request_info() -> dict:
    return {
        "endpoint": "users",
        "params": {"max": 500},
        "url_key": "keycloak"
    }


def _get_user_request_info(user_id: str) -> dict:
    return {
        "endpoint": f"users/{user_id}",
        "url_key": "keycloak"
    }


def _update_user_request_info(user_id: str, data: dict) -> dict:
    return {
        "endpoint": f"users/{user_id}",
        "url_key": "keycloak",
        "json": data
    }


def _get_groups_request_info() -> dict:
    return {
        "endpoint": "groups",
        "url_key": "keycloak"
    }


def _get_group_members_request_info(id: str) -> dict:
    return {
        "endpoint": f"groups/{id}/members",
        "url_key": "keycloak"
    }


def _add_group_to_user_request_info(user_id: str, group_id: str) -> dict:
    return {
        "endpoint": f"users/{user_id}/groups/{group_id}",
        "url_key": "keycloak"
    }


def _delete_group_from_user_request_info(user_id: str, group_id: str) -> dict:
    return {
        "endpoint": f"users/{user_id}/groups/{group_id}",
        "url_key": "keycloak"
    }


def _get_roles_request_info() -> dict:
    return {
        "endpoint": "roles",
        "url_key": "keycloak"
    }


def _get_roles_for_user_request_info(user_id: str) -> dict:
    return {
        "endpoint": f"users/{user_id}/role-mappings",
        "url_key": "keycloak"
    }


def _add_role_mapping_to_user_request_info(user_id: str, role_ids: List[Dict[str, str]]) -> dict:
    return {
        "endpoint": f"users/{user_id}/role-mappings/realm",
        "url_key": "keycloak",
        "json": role_ids
    }

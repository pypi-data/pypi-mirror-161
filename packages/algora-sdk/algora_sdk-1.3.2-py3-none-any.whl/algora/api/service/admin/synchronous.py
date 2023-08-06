from typing import List, Dict

from algora.api.service.admin.__util import (
    _get_client_id_request_info, _get_users_request_info, _get_user_request_info, _update_user_request_info,
    _get_groups_request_info, _get_group_members_request_info, _add_group_to_user_request_info,
    _delete_group_from_user_request_info, _get_roles_request_info, _get_roles_for_user_request_info,
    _add_role_mapping_to_user_request_info
)
from algora.common.decorators import data_request
from algora.common.function import no_transform
from algora.common.requests import (
    __get_request, __put_request, __post_request, __delete_request
)


@data_request(transformer=no_transform)
def get_client_id():
    """
    Get keycloak client ID.

    Returns:
        Keycloak client ID.
    """
    request_info = _get_client_id_request_info()
    return __get_request(**request_info)


@data_request
def get_users():
    """
    Get all users.

    Returns:
        List of user response.
    """
    request_info = _get_users_request_info()
    return __get_request(**request_info)


@data_request(transformer=no_transform)
def get_user(user_id: str):
    """
    Get user by ID.

    Args:
        user_id (str): User ID

    Returns:
        User response
    """
    request_info = _get_user_request_info(user_id)
    return __get_request(**request_info)


@data_request(transformer=no_transform, processor=lambda r: r)
def update_user(user_id: str, data: dict):
    """
    Update user.

    Args:
        user_id (str): User ID
        data (dict): User request

    Returns:
        User response
    """
    request_info = _update_user_request_info(user_id, data)
    return __put_request(**request_info)


@data_request(transformer=no_transform)
def get_groups():
    """
    Get groups.

    Returns:
        List of groups.
    """
    request_info = _get_groups_request_info()
    return __get_request(**request_info)


@data_request(transformer=no_transform)
def get_group_members(id: str):
    """
    Get group members given group ID.

    Args:
        id (str): Group ID

    Returns:
        List of user response
    """
    request_info = _get_group_members_request_info(id)
    return __get_request(**request_info)


@data_request(transformer=no_transform, processor=lambda r: r)
def add_group_to_user(user_id: str, group_id: str):
    """
    Add user to group.

    Args:
        user_id (str): User ID
        group_id (str): Group ID

    Returns:
        None
    """
    request_info = _add_group_to_user_request_info(user_id, group_id)
    return __put_request(**request_info)


@data_request(transformer=no_transform, processor=lambda r: r)
def delete_group_from_user(user_id: str, group_id: str):
    """
    Delete user from group.

    Args:
        user_id (str): User ID
        group_id (str): Group ID

    Returns:
        None
    """
    request_info = _delete_group_from_user_request_info(user_id, group_id)
    return __delete_request(**request_info)


@data_request(transformer=no_transform)
def get_roles():
    """
    Get roles.

    Returns:
        List of role response.
    """
    request_info = _get_roles_request_info()
    return __get_request(**request_info)


@data_request(transformer=no_transform)
def get_roles_for_user(user_id: str):
    """
    Get roles for user.

    Args:
        user_id (str): User ID

    Returns:
        List of role response
    """
    request_info = _get_roles_for_user_request_info(user_id)
    return __get_request(**request_info)


@data_request(transformer=no_transform, processor=lambda r: r)
def add_role_mapping_to_user(user_id: str, role_ids: List[Dict[str, str]]):
    """
    Add role mapping to user.

    Args:
        user_id (str): User ID
        role_ids (List[Dict[str, str]]): List of role ID mapping

    Returns:
        None
    """
    request_info = _add_role_mapping_to_user_request_info(user_id, role_ids)
    return __post_request(**request_info)

"""
Keycloak API requests.
"""
from typing import List, Dict

from algora.api.service.admin.__util import (
    _get_client_id_request_info, _get_users_request_info, _get_user_request_info, _update_user_request_info,
    _get_groups_request_info, _get_group_members_request_info, _add_group_to_user_request_info,
    _delete_group_from_user_request_info, _get_roles_request_info, _get_roles_for_user_request_info,
    _add_role_mapping_to_user_request_info
)
from algora.common.decorators import async_data_request
from algora.common.function import no_transform
from algora.common.requests import (
    __async_get_request, __async_put_request, __async_post_request, __async_delete_request
)


@async_data_request(transformer=no_transform)
async def async_get_client_id():
    """
    Asynchronously get keycloak client ID.

    Returns:
        Keycloak client ID.
    """
    request_info = _get_client_id_request_info()
    return await __async_get_request(**request_info)


@async_data_request
async def async_get_users():
    """
    Asynchronously get all users.

    Returns:
        List of user response.
    """
    request_info = _get_users_request_info()
    return await __async_get_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_get_user(user_id: str):
    """
    Asynchronously get user by ID.

    Args:
        user_id (str): User ID

    Returns:
        User response
    """
    request_info = _get_user_request_info(user_id)
    return await __async_get_request(**request_info)


@async_data_request(transformer=no_transform, processor=lambda r: r)
async def async_update_user(user_id: str, data: dict):
    """
    Asynchronously update user.

    Args:
        user_id (str): User ID
        data (dict): User request

    Returns:
        User response
    """
    request_info = _update_user_request_info(user_id, data)
    return await __async_put_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_get_groups():
    """
    Asynchronously get groups.

    Returns:
        List of groups.
    """
    request_info = _get_groups_request_info()
    return await __async_get_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_get_group_members(id: str):
    """
    Asynchronously get group members given group ID.

    Args:
        id (str): Group ID

    Returns:
        List of user response
    """
    request_info = _get_group_members_request_info(id)
    return await __async_get_request(**request_info)


@async_data_request(transformer=no_transform, processor=lambda r: r)
async def async_add_group_to_user(user_id: str, group_id: str):
    """
    Asynchronously add user to group.

    Args:
        user_id (str): User ID
        group_id (str): Group ID

    Returns:
        None
    """
    request_info = _add_group_to_user_request_info(user_id, group_id)
    return await __async_put_request(**request_info)


@async_data_request(transformer=no_transform, processor=lambda r: r)
async def async_delete_group_from_user(user_id: str, group_id: str):
    """
    Asynchronously delete user from group.

    Args:
        user_id (str): User ID
        group_id (str): Group ID

    Returns:
        None
    """
    request_info = _delete_group_from_user_request_info(user_id, group_id)
    return await __async_delete_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_get_roles():
    """
    Asynchronously get roles.

    Returns:
        List of role response.
    """
    request_info = _get_roles_request_info()
    return await __async_get_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_get_roles_for_user(user_id: str):
    """
    Asynchronously get roles for user.

    Args:
        user_id (str): User ID

    Returns:
        List of role response
    """
    request_info = _get_roles_for_user_request_info(user_id)
    return await __async_get_request(**request_info)


@async_data_request(transformer=no_transform, processor=lambda r: r)
async def async_add_role_mapping_to_user(user_id: str, role_ids: List[Dict[str, str]]):
    """
    Asynchronously add role mapping to user.

    Args:
        user_id (str): User ID
        role_ids (List[Dict[str, str]]): List of role ID mapping

    Returns:
        None
    """
    request_info = _add_role_mapping_to_user_request_info(user_id, role_ids)
    return await __async_post_request(**request_info)

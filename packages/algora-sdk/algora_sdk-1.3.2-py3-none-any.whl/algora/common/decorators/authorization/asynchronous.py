"""
Authorization decorators.
"""
import functools
from typing import Any, Callable, Optional

import aiohttp
from aiocache.decorators import cached
from aiohttp import ClientResponse
from requests import Response

from algora.common.config import EnvironmentConfig
from algora.common.decorators.authorization.__util import (
    _access_token, _sign_in_request_info, _handle_auth_response, _refresh_token_request_info, _validate_headers
)


async def build_response_obj(aio_response: ClientResponse) -> Response:
    """
    Construct a requests Response object from an aiohttp Client Response object

    Args:
        aio_response (ClientResponse): Response object from aiohttp

    Returns:
        Response: A requests Response object
    """
    content = await aio_response.content.read()

    response = Response()
    response._content = content
    response.url = str(aio_response.url)
    response.status_code = aio_response.status
    headers = {row[0]: row[1] for row in aio_response.headers.items()}
    response.headers = headers
    return response


def async_authenticated_request(
        request: Callable = None,
        *,
        env_config: Optional[EnvironmentConfig] = None
) -> Callable:
    """
    Decorator for requests that need to be authenticated

    Args:
          request (Callable): Method that needs auth headers injected
          env_config (Optional[EnvironmentConfig]): Optional environment config
    Returns:
        Callable: Wrapped function
    """

    @functools.wraps(request)
    def decorator(f):
        @functools.wraps(f)
        async def wrap(*args, **kwargs) -> Any:
            """
            Wrapper for the decorated function

            Args:
                *args: args for the function
                **kwargs: keyword args for the function

            Returns:
                Any: The output of the wrapped function
            """
            config = env_config if env_config is not None else EnvironmentConfig()
            headers = kwargs.get("headers", {})

            if config.auth_config.can_authenticate():
                auth_headers = await _authenticate(
                    base_url=config.get_url(),
                    username=config.auth_config.username,
                    password=config.auth_config.password,
                    access_token=config.auth_config.access_token,
                    refresh_token=config.auth_config.refresh_token
                )
                auth_headers.update(headers)  # override authentication header if already provided
                kwargs["headers"] = auth_headers

            return await _make_request(f, config, *args, **kwargs)

        return wrap

    if request is None:
        return decorator
    return decorator(request)


@cached(ttl=1740)
async def _authenticate(
        base_url: Optional[str],
        username: Optional[str],
        password: Optional[str],
        access_token: Optional[str],
        refresh_token: Optional[str]
) -> dict:
    """
    Asynchronously authenticate user and create user authentication headers.

    Args:
        base_url (Optional[str]): Base request URL
        username (Optional[str]): Algora username
        password (Optional[str]): Algora password
        access_token (Optional[str]): Algora access token
        refresh_token (Optional[str]): Algora refresh token

    Returns:
        dict: Auth headers for a request
    """
    auth_headers = {}
    if username and password:
        auth_headers = await _sign_in(
            base_url=base_url,
            username=username,
            password=password
        )
    elif access_token:
        auth_headers = _access_token(access_token)
    elif refresh_token:
        auth_headers = await _refresh_token(base_url, refresh_token)
    return auth_headers


async def _sign_in(base_url: str, username: str, password: str) -> dict:
    request_info = _sign_in_request_info(base_url, username, password)
    async with aiohttp.ClientSession() as session:
        async with session.post(**request_info) as response:
            auth_response = await build_response_obj(response)
    return _handle_auth_response(auth_response, error_msg="Failed to sign-in the user")


async def _refresh_token(base_url: str, refresh_token: Optional[str] = None) -> dict:
    request_info = _refresh_token_request_info(base_url, refresh_token)
    async with aiohttp.ClientSession() as session:
        async with session.post(**request_info) as response:
            auth_response = await build_response_obj(response)
    return _handle_auth_response(auth_response, error_msg="Failed to refresh the user's token")


async def _make_request(func, config: EnvironmentConfig, *args, **kwargs) -> Response:
    _validate_headers(**kwargs)

    response: Response = await func(*args, **kwargs)
    if response.status_code == 401 and config.auth_config.refresh_token:
        auth_headers = await _refresh_token(config.get_url(), config.auth_config.refresh_token)
        kwargs['headers'].update(auth_headers)  # override authentication header
        response: Response = await func(*args, **kwargs)

    return response

import functools
from typing import Optional, Callable, Tuple, Dict, Any

from typing_extensions import Literal

from algora.common.data_provider import Provider, AsyncProvider
from algora.common.model import DataRequest


def provider(
        get_data_method: Callable[[DataRequest], Any] = None,
        *,
        name: Optional[str] = None,
        provider_type: Literal['sync', 'async'] = 'sync'
):
    """
    Data provider function, containing name and asynchronous get_data functionality. Alternative to creating a Provider
    class.

    Args:
        get_data_method (Callable[[DataRequest], Any]): Data request-response function to wrap
        name (Optional[str]): Data provider name
        provider_type (Literal['sync', 'async']): Type of provider, either synchronous or asynchronous

    Returns:
        An synchronous or asynchronous provider class containing the decorated method
    """

    @functools.wraps(get_data_method)
    def decorator(f):
        @functools.wraps(f)
        def wrap(*args: Tuple, **kwargs: Dict[str, Any]):
            """
            Wrapper for the decorated function.

            Args:
                *args: args for the function
                **kwargs: keyword args for the function

            Returns:

            """
            provider_cls = AsyncProvider if provider_type == 'async' else Provider
            cls = type(name, (provider_cls,), {})
            setattr(cls, "get_data", f)
            setattr(cls, "name", lambda: name)
            return cls

        return wrap

    if get_data_method is None:
        return decorator
    return decorator(get_data_method)

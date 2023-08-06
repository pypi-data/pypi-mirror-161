import functools
from typing import Tuple, Dict, Any, Callable

import pandas as pd
from requests import Response

from algora.common.decorators.data.__util import __process_response


def async_data_request(
        request: Callable = None,
        *,
        processor: Callable[[Response], Any] = lambda response: response.json(),
        transformer: Callable[[Any], Any] = lambda data: pd.DataFrame(data)
):
    """
    Decorator for processing the response of an asynchronous REST request.

    Args:
        request (Callable): Function
        processor (Callable[[Response], Any]): Transform response
        transformer (Callable[[Any], Any]): Transform data output

    Returns:
        Callable: Wrapped function
    """

    @functools.wraps(request)
    def decorator(f):
        @functools.wraps(f)
        async def wrap(*args: Tuple, **kwargs: Dict[str, Any]) -> Any:
            _processor = kwargs.pop('processor', None) or processor
            _transformer = kwargs.pop('transformer', None) or transformer
            response: Response = await f(*args, **kwargs)
            return __process_response(response, _processor, _transformer)

        return wrap

    if request is None:
        return decorator
    return decorator(request)

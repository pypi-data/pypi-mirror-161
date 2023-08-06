import functools
from typing import Tuple, Dict, Any, Callable

import pandas as pd
from requests import Response

from algora.common.decorators.data.__util import __process_response


def data_request(
        request: Callable = None,
        *,
        processor: Callable[[Response], Any] = lambda response: response.json(),
        transformer: Callable[[Any], Any] = lambda data: pd.DataFrame(data)
) -> Callable:
    """
    Decorator for processing the response of a REST request.

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
        def wrap(*args: Tuple, **kwargs: Dict[str, Any]) -> Any:
            _processor = kwargs.pop('processor', None) or processor
            _transformer = kwargs.pop('transformer', None) or transformer
            response: Response = f(*args, **kwargs)
            return __process_response(response, _processor, _transformer)

        return wrap

    if request is None:
        return decorator
    return decorator(request)

import logging
from typing import Any, Callable

from requests import Response

from algora.common.errors import ApiError

logger = logging.getLogger(__name__)


def __process_response(
        response: Response,
        processor: Callable[[Response], Any],
        transformer: Callable[[Any], Any]
):
    if response.status_code != 200 | response.status_code != 201:
        error = ApiError(
            f"Request to {response.url} failed with status code {response.status_code}: {response.text}"
        )
        logger.error(error)
        raise error

    data = processor(response)
    return transformer(data)

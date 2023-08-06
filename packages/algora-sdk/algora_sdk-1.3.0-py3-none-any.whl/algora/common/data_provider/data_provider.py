import asyncio
from typing import Iterable, Dict, List

from algora.common.data_provider.abstract import Provider, AsyncProvider
from algora.common.model import DataRequest
from algora.common.type import DataResponse


class DataProvider:
    """
    Data provider wrapper class which holds Provider classes and provider functions and performs data querying.
    """

    class _Builder:
        def __init__(self):
            self._blocking_providers = []
            self._async_providers = []

        @classmethod
        def new_instance(cls):
            return cls()

        def build(self):
            return DataProvider(self._blocking_providers, self._async_providers)

        def blocking_providers(self, *providers):
            self._blocking_providers = [_provider() for _provider in providers]
            return self

        def async_providers(self, *providers):
            self._async_providers = [_provider() for _provider in providers]
            return self

    @classmethod
    def builder(cls) -> _Builder:
        return cls._Builder.new_instance()

    def __init__(
            self,
            blocking_providers: Iterable[Provider],
            async_providers: Iterable[AsyncProvider]
    ):
        self.blocking_providers = blocking_providers
        self.async_providers = async_providers

    async def get_data(self, request: DataRequest) -> Dict[str, DataResponse]:
        """
        Query all data providers and return dict of name to data response. Uses asynchronous providers if provided,
        else uses synchronous providers.

        Args:
            request (DataRequest): Data request

        Returns:
            Dict[str, DataResponse]: Dict of name to data response
        """
        async_provider_names = [_provider.name() for _provider in self.async_providers]
        async_data = await self.get_async_data(request)
        data = self.get_blocking_data(request, names_to_skip=async_provider_names)
        data.update(async_data)
        return data

    def get_blocking_data(self, request: DataRequest, names_to_skip: List[str] = None) -> Dict[str, DataResponse]:
        """
        Query all data providers and return dict of name to data response.

        Args:
            request (DataRequest): Data request
            names_to_skip (List[str]): List of data providers to skip when querying

        Returns:
            Dict[str, DataResponse]: Dict of name to data response
        """
        names_to_skip = [] if names_to_skip is None else names_to_skip
        return {
            _provider.name(): _provider.get_data(request)
            for _provider in self.blocking_providers if _provider.name() not in names_to_skip
        }

    async def get_async_data(self, request: DataRequest) -> Dict[str, DataResponse]:
        """
        Asynchronously query all data providers and return dict of name to data response.

        Args:
            request (DataRequest): Data request

        Returns:
            Dict[str, DataResponse]: Dict of name to data response
        """

        # TODO: Make a helper in algoralabs sdk
        async def key_value_coroutine(_provider):
            key = _provider.name()
            value = await _provider.get_data(request)
            return key, value

        coroutines = [key_value_coroutine(_provider) for _provider in self.async_providers]
        result = await asyncio.gather(*coroutines)
        return dict(result)

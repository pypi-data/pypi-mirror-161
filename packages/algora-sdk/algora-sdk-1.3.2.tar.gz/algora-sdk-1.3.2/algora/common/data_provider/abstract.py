from abc import abstractmethod, ABC

from algora.common.model import DataRequest
from algora.common.type import DataResponse


class Provider(ABC):
    """
    Data provider class, containing name and get_data methods.
    """

    @abstractmethod
    def name(self) -> str:
        """
        Data provider name.

        Returns:
            str: Data provider name
        """
        pass

    @abstractmethod
    def get_data(self, request: DataRequest) -> DataResponse:
        """
        Get data and return result.

        Args:
            request (DataRequest): Data request class

        Returns:
            DataResponse: Data response
        """
        pass


class AsyncProvider(ABC):
    """
    Asynchronous data provider class, containing name and asynchronous get_data methods.
    """

    @abstractmethod
    def name(self) -> str:
        """
        Data provider name.

        Returns:
            str: Data provider name
        """
        pass

    @abstractmethod
    async def get_data(self, request: DataRequest) -> DataResponse:
        """
        Asynchronously get data and return result.

        Args:
            request (DataRequest): Data request class

        Returns:
            DataResponse: Data response
        """
        pass

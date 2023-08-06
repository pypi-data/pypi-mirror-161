import abc
from databricks_cli.sdk import ApiClient

from whizbang.domain.shared_types.api_methods import ApiMethods
from whizbang.domain.shared_types.databricks_api_paths import DatabricksApiPaths


class IDatabricksContextBase(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def _execute(self, func, **kwargs):
        """interface method for execute databricks cli command"""


class DatabricksContextBase(IDatabricksContextBase):
    """This base class allows for the direct calling of databricks cli functions."""
    def __init__(self, api_client: ApiClient, api):
        self.__client = api_client
        self.__api = api

    def _execute(self, func, **kwargs):
        result = func(self.__api, **kwargs)
        self.__client.close()

        return result


class DatabricksApiContextBase:
    """This base class allows an arbitrary query to be run against the databricks api.
    Use only when no cli wrapper has been added to the databricks cli yet."""
    def __init__(self, api_client: ApiClient):
        self._api_methods = ApiMethods
        self._databricks_api_paths = DatabricksApiPaths
        self.__client = api_client

    def _query(self, method, path: str, data: dict):
        result = self.__client.perform_query(method=method, path=path, data=data)
        self.__client.close()
        return result

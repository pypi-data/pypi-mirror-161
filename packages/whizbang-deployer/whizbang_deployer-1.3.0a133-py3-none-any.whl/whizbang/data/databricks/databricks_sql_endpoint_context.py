
from databricks_cli.sdk import ApiClient

from whizbang.data.databricks.databricks_context_base import DatabricksApiContextBase


class DatabricksSqlEndpointContext(DatabricksApiContextBase):
    def __init__(self, api_client: ApiClient):
        super().__init__(api_client=api_client)

    def create_endpoint(self, sql_endpoint: dict) -> dict:
        sql_endpoint = self._query(method=self._api_methods.post,
                                   path=self._databricks_api_paths.sql_endpoint,
                                   data=sql_endpoint)
        return sql_endpoint

    def get_endpoints(self) -> dict:
        sql_endpoints = self._query(method=self._api_methods.get,
                                    path=self._databricks_api_paths.sql_endpoint,
                                    data={})
        return sql_endpoints

    def edit_endpoint(self, sql_endpoint: dict, endpoint_id: str) -> dict:
        sql_endpoint = self._query(method=self._api_methods.post,
                                   path=f'{self._databricks_api_paths.sql_endpoint}/{endpoint_id}/edit',
                                   data=sql_endpoint)
        return sql_endpoint



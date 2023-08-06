from whizbang.data.databricks.databricks_client_args import DatabricksClientArgs
from whizbang.data.databricks.databricks_context_factory import DatabricksContextFactory
from whizbang.domain.models.databricks.databricks_sql_endpoint import DatabricksSqlEndpoint
from whizbang.domain.repository.databricks.databricks_repository_base import DatabricksRepositoryBase
from whizbang.domain.shared_types.databricks_api_type import DatabricksApiType


class DatabricksSqlEndpointRepository(DatabricksRepositoryBase):
    def __init__(self, context_factory: DatabricksContextFactory):
        DatabricksRepositoryBase.__init__(self, context_factory)

    @property
    def context_type(self) -> str: return DatabricksApiType.sql_endpoint

    def create(self, client_args: DatabricksClientArgs, t_object: DatabricksSqlEndpoint) -> dict:
        context = self._get_context(client_args)
        return context.create_endpoint(
            sql_endpoint=t_object.sql_endpoint_dict
        )

    def get(self, client_args: DatabricksClientArgs) -> dict:
        context = self._get_context(context_args=client_args)

        return context.get_endpoints()

    def edit(self, client_args: DatabricksClientArgs, t_object: DatabricksSqlEndpoint, endpoint_id: str) -> dict:
        context = self._get_context(client_args)
        return context.edit_endpoint(
            sql_endpoint=t_object.sql_endpoint_dict,
            endpoint_id=endpoint_id
        )

    def update(self, client_args: DatabricksClientArgs, t_object):
        pass

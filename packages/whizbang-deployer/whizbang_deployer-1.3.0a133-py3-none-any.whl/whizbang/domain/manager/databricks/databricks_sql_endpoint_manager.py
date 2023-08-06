from whizbang.data.databricks.databricks_client_args import DatabricksClientArgs
from whizbang.domain.manager.databricks.databricks_manager_base import DatabricksManagerBase
from whizbang.domain.models.databricks.databricks_sql_endpoint import DatabricksSqlEndpoint

from whizbang.domain.repository.databricks.databricks_sql_endpoint_repository import DatabricksSqlEndpointRepository


class DatabricksSqlEndpointManager(DatabricksManagerBase):
    def __init__(self, repository: DatabricksSqlEndpointRepository):
        DatabricksManagerBase.__init__(self, repository)

    def save(self, client_args: DatabricksClientArgs, t_object: DatabricksSqlEndpoint):
        existing_endpoints: dict = self.repository.get(client_args=client_args)
        for endpoint in existing_endpoints.get("endpoints"):
            if endpoint.get("name") == t_object.sql_endpoint_dict.get("name"):
                return self.repository.edit(client_args=client_args, t_object=t_object, endpoint_id=endpoint.get("id"))
            else:
                return self.repository.create(client_args=client_args, t_object=t_object)

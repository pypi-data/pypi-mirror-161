from whizbang.data.databricks.databricks_client_args import DatabricksClientArgs
from whizbang.domain.manager.databricks.databricks_manager_base import DatabricksManagerBase
from whizbang.domain.models.databricks.databricks_file import DatabricksFile
from whizbang.domain.repository.databricks.databricks_filesystem_repository import DatabricksFilesystemRepository


class DatabricksFilesystemManager(DatabricksManagerBase):
    def __init__(self, repository: DatabricksFilesystemRepository):
        DatabricksManagerBase.__init__(self, repository)
        self.repository: DatabricksFilesystemRepository

    def save(self, client_args: DatabricksClientArgs, file: DatabricksFile):
        result = self.repository.create(client_args=client_args,
                                        t_object=file)
        return result

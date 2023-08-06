from databricks_cli.dbfs.dbfs_path import DbfsPath

from whizbang.data.databricks.databricks_client_args import DatabricksClientArgs
from whizbang.data.databricks.databricks_context_factory import IDatabricksContextFactory
from whizbang.data.databricks.databricks_filesystem_context import DatabricksFilesystemContext
from whizbang.domain.models.databricks.databricks_file import DatabricksFile
from whizbang.domain.repository.databricks.databricks_repository_base import DatabricksRepositoryBase
from whizbang.domain.shared_types.databricks_api_type import DatabricksApiType


class DatabricksFilesystemRepository(DatabricksRepositoryBase):
    def __init__(self, context_factory: IDatabricksContextFactory):
        DatabricksRepositoryBase.__init__(self, databricks_context_factory=context_factory)

    @property
    def context_type(self) -> str: return DatabricksApiType.databricks_file_system

    def create(self, client_args: DatabricksClientArgs, t_object: DatabricksFile):
        context: DatabricksFilesystemContext = self._get_context(client_args)
        dbfs_path = DbfsPath(absolute_path=t_object.destination_path)
        result = context.upload_file(
            source_path=t_object.source_path,
            dbfs_path=dbfs_path,
            overwrite=t_object.overwrite
        )
        return result

    def get(self, client_args: DatabricksClientArgs):
        pass

    def update(self, client_args: DatabricksClientArgs, t_object):
        pass

from databricks_cli.dbfs.api import DbfsApi
from databricks_cli.dbfs.dbfs_path import DbfsPath
from databricks_cli.sdk import ApiClient

from whizbang.data.databricks.databricks_context_base import DatabricksContextBase


class DatabricksFilesystemContext(DatabricksContextBase):
    def __init__(self, api_client: ApiClient, api):
        DatabricksContextBase.__init__(self, api_client=api_client, api=api)

    def upload_file(self, source_path: str, dbfs_path: DbfsPath, overwrite: bool):
        def _upload_file(api: DbfsApi, source_path: str, dbfs_path: str, overwrite: bool):
            return api.put_file(src_path=source_path, dbfs_path=dbfs_path, overwrite=overwrite)

        return self._execute(func=_upload_file, source_path=source_path, dbfs_path=dbfs_path,
                             overwrite=overwrite)

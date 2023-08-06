from typing import List

from whizbang.domain.models.storage.storage_resource import StorageContainer


class DatalakeState:
    def __init__(self,
                 datalake_json: dict,
                 storage_container: StorageContainer,
                 recursive: bool = True,
                 permissions: str = "r",
                 path: str = ''"/"''):
        self.storage_container = storage_container
        self.datalake_json = datalake_json
        self.recursive = recursive
        self.permissions = permissions
        self.path = path

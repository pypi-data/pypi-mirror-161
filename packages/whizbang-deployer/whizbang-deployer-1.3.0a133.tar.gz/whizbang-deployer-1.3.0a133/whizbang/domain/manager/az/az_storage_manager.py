from abc import abstractmethod
from typing import Dict, List

from whizbang.domain.manager.az.az_resource_manager_base import IAzResourceManager, AzResourceManagerBase
from whizbang.domain.models.firewall_rule_cidr import FirewallRuleCIDR
from whizbang.domain.models.storage.storage_network_rule import StorageIPNetworkRule, StorageVnetIPNetworkRule
from whizbang.domain.models.storage.storage_resource import StorageAccountResource, StorageContainer, StorageBlobSource, \
    StorageDatalakeSource
from whizbang.domain.repository.az.az_storage_repository import IAzStorageRepository


class IAzStorageManager(IAzResourceManager):

    @abstractmethod
    def create_account(self, storage_account: StorageAccountResource):
        """"""

    @abstractmethod
    def create_container(self, storage_container: StorageContainer):
        """"""

    @abstractmethod
    def upload_blob(self, storage_blob: StorageBlobSource):
        """"""

    @abstractmethod
    def download_blob(self, storage_blob: StorageBlobSource):
        """"""

    @abstractmethod
    def create_file_system(self, file_system: StorageContainer):
        """"""

    @abstractmethod
    def upload_datalake_directory(self, directory_source: StorageDatalakeSource):
        """"""

    @abstractmethod
    def create_datalake_directories(self, directories: List[Dict],
                                    storage_container: StorageContainer,
                                    name: str = None):
        """"""

    @abstractmethod
    def create_datalake_directory(self, directory_source: StorageDatalakeSource):
        """"""

    @abstractmethod
    def set_datalake_container_acl(self, datalake_container: StorageContainer, object_id: str,
                                   permissions: str, path: str = '"/"'):
        """"""

    @abstractmethod
    def update_datalake_container_acl(self, datalake_container: StorageContainer, object_id: str,
                                      permissions: str, path: str = '"/"'):
        """"""

    @abstractmethod
    def remove_datalake_container_acl(self, datalake_container: StorageContainer, object_id: str,
                                      path: str = '"/"'):
        """"""

    @abstractmethod
    def get_storage_account_key(self, storage_account_name: str) -> str:
        """"""

    @abstractmethod
    def add_ip_network_rule(self, storage_ip_network_rule: StorageIPNetworkRule):
        """"""

    @abstractmethod
    def remove_ip_network_rule(self, storage_ip_network_rule: StorageIPNetworkRule):
        """"""

    @abstractmethod
    def add_vnet_network_rule(self, storage_vnet_network_rule: StorageVnetIPNetworkRule):
        """"""

    @abstractmethod
    def remove_vnet_network_rule(self, storage_vnet_network_rule: StorageVnetIPNetworkRule):
        """"""

    @abstractmethod
    def update_account_networking(self, storage_account_name: str, allow: bool):
        """"""


class AzStorageManager(AzResourceManagerBase, IAzStorageManager):
    def __init__(self, repository: IAzStorageRepository):
        AzResourceManagerBase.__init__(self, repository=repository)
        self._repository: IAzStorageRepository

    def create_account(self, storage_account: StorageAccountResource):
        return self._repository.create_account(storage_account=storage_account)

    def create_container(self, storage_container: StorageContainer):
        return self._repository.create_container(storage_container=storage_container)

    def upload_blob(self, storage_blob: StorageBlobSource):
        return self._repository.upload_blob(storage_blob=storage_blob)

    def download_blob(self, storage_blob: StorageBlobSource):
        return self._repository.download_blob(storage_blob=storage_blob)

    def create_file_system(self, file_system: StorageContainer):
        return self._repository.create_file_system(file_system=file_system)

    def upload_datalake_directory(self, directory_source: StorageDatalakeSource):
        return self._repository.upload_datalake_directory(directory_source=directory_source)

    def create_datalake_directories(self, directories: List[Dict],
                                    storage_container: StorageContainer,
                                    name: str = None):
        name = name or ''
        for directory in directories:
            datalake_directory = StorageDatalakeSource(local_path=f'{name}/{directory["directory"]}',
                                                       container_name=storage_container.container_name,
                                                       storage_account_name=storage_container.storage_account_name)
            self.create_datalake_directory(directory_source=datalake_directory)
            if directory['subdirectories'] is not None:
                self.create_datalake_directories(directories=directory['subdirectories'],
                                                 name=f'{name}/{directory["directory"]}',
                                                 storage_container=storage_container)

    def create_datalake_directory(self, directory_source: StorageDatalakeSource):
        return self._repository.create_datalake_directory(directory_source=directory_source)

    def set_datalake_container_acl(self, datalake_container: StorageContainer, object_id: str, permissions: str = 'r',
                                   path: str = '"/"'):
        """
        :param datalake_container: The container information where the acls will be set
        :param object_id: Id of the object to be added to the access control list
        :param permissions: r, w and x permissions to be applied for the object id
        :param path: path to where the acls should be applied in the filesystem
        :return: The CLI response of the created acls
        """
        key = self.get_storage_account_key(storage_account_name=datalake_container.storage_account_name)
        datalake_container.account_key = key
        return self._repository.set_datalake_container_acl(datalake_container=datalake_container,
                                                           object_id=object_id,
                                                           permissions=permissions,
                                                           path=path)

    def update_datalake_container_acl(self, datalake_container: StorageContainer, object_id: str,
                                      permissions: str = 'r', path: str = '"/"'):
        """
        Recursively updates datalake acls
        :param datalake_container: The container information where the acls will be set
        :param object_id: Id of the object to be added to the access control list
        :param permissions: r, w and x permissions to be applied for the object id
        :param path: path to where the acls should be applied in the filesystem
        :return: The CLI response of the created acls
        """
        key = self.get_storage_account_key(storage_account_name=datalake_container.storage_account_name)
        datalake_container.account_key = key
        return self._repository.update_datalake_container_acl(datalake_container=datalake_container,
                                                              object_id=object_id,
                                                              permissions=permissions,
                                                              path=path)

    def remove_datalake_container_acl(self, datalake_container: StorageContainer, object_id: str,
                                      path: str = '"/"'):
        """
        Recursively removes datalake acls
        :param datalake_container: The container information where the acls will be removed
        :param object_id: Id of the object to be removed from the access control list
        :param path: path to where the acls should be removed from the filesystem
        :return: The CLI response of the removed acls
        """
        key = self.get_storage_account_key(storage_account_name=datalake_container.storage_account_name)
        datalake_container.account_key = key
        return self._repository.remove_datalake_container_acl(datalake_container=datalake_container,
                                                              object_id=object_id,
                                                              path=path)

    def get_storage_account_key(self, storage_account_name: str) -> str:
        return self._repository.get_storage_account_key(storage_account_name=storage_account_name)

    def add_ip_network_rule(self, storage_ip_network_rule: StorageIPNetworkRule):
        return self._repository.add_ip_network_rule(storage_ip_network_rule=storage_ip_network_rule)

    def remove_ip_network_rule(self, storage_ip_network_rule: StorageIPNetworkRule):
        return self._repository.remove_ip_network_rule(storage_ip_network_rule=storage_ip_network_rule)

    def add_vnet_network_rule(self, storage_vnet_network_rule: StorageVnetIPNetworkRule):
        return self._repository.add_vnet_network_rule(storage_vnet_network_rule=storage_vnet_network_rule)

    def remove_vnet_network_rule(self, storage_vnet_network_rule: StorageVnetIPNetworkRule):
        return self._repository.remove_vnet_network_rule(storage_vnet_network_rule=storage_vnet_network_rule)

    def update_account_networking(self, storage_account_name: str, allow: bool):
        return self._repository.update_account_networking(storage_account_name=storage_account_name,
                                                          allow=allow)

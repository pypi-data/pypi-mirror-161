from abc import abstractmethod

from whizbang.data.az_cli_context import AzCliContext
from whizbang.domain.models.firewall_rule_cidr import FirewallRuleCIDR
from whizbang.domain.models.storage.storage_network_rule import StorageIPNetworkRule, StorageVnetIPNetworkRule
from whizbang.domain.models.storage.storage_resource import StorageAccountResource, StorageContainer, StorageBlobSource, \
    StorageDatalakeSource
from whizbang.domain.repository.az.az_active_directory_repository import IAzActiveDirectoryRepository
from whizbang.domain.repository.az.az_resource_repository_base import IAzResourceRepository, AzResourceRepositoryBase


class IAzStorageRepository(IAzResourceRepository):
    """the AzStorageRepository interface"""

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
    def create_datalake_directory(self, directory_source: StorageDatalakeSource):
        """"""

    @abstractmethod
    def update_datalake_container_acl(self, datalake_container: StorageContainer, object_id: str,
                                      permissions: str):
        """"""

    @abstractmethod
    def remove_datalake_container_acl(self, datalake_container: StorageContainer, object_id: str):
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


class AzStorageRepository(AzResourceRepositoryBase, IAzStorageRepository):

    def __init__(self, context: AzCliContext, active_directory_repository: IAzActiveDirectoryRepository):
        AzResourceRepositoryBase.__init__(self, context)
        self.active_directory_repository = active_directory_repository

    @property
    def _resource_provider(self) -> str:
        return 'storage'

    def create(self, resource: StorageAccountResource):
        return self.create_account(resource)

    def create_account(self, storage_account: StorageAccountResource):
        response = self._execute(f'account create --name {storage_account.resource_name}'
                                 f' --resource-group {storage_account.resource_group_name}'
                                 f' --location {storage_account.location}')

        return response.results

    def create_container(self, storage_container: StorageContainer):
        response = self._execute(f'container create --name {storage_container.container_name}'
                                 f' --account-name {storage_container.storage_account_name}')
        return response.results

    def upload_blob(self, storage_blob: StorageBlobSource):
        command = f'blob upload --name {storage_blob.name}' \
                    f' --file {storage_blob.local_path}' \
                    f' --container-name {storage_blob.container_name}' \
                    f' --account-name {storage_blob.storage_account_name}'
        if storage_blob.tier:
            command += f' --tier {storage_blob.tier}'
        response = self._execute(command)
        return response.results

    def download_blob(self, storage_blob: StorageBlobSource):
        response = self._execute(f'blob download --name {storage_blob.name}'
                                 f' --file {storage_blob.local_path}'
                                 f' --container-name {storage_blob.container_name}'
                                 f' --account-name {storage_blob.storage_account_name}')
        return response.results

    def file_system_exists(self, file_system: StorageContainer) -> bool:
        response = self._execute(f'fs exists --name {file_system.container_name}'
                                 f' --account-name {file_system.storage_account_name}'
                                 f' --auth-mode login')

        return response.results.get('exists')

    def get_file_system(self, file_system: StorageContainer) -> bool:
        response = self._execute(f'fs show --name {file_system.container_name}'
                                 f' --account-name {file_system.storage_account_name}'
                                 f' --auth-mode login')
        return response.results

    def create_file_system(self, file_system: StorageContainer):
        if self.file_system_exists(file_system):
            return self.get_file_system(file_system)

        response = self._execute(f'fs create --name {file_system.container_name}'
                                 f' --account-name {file_system.storage_account_name}'
                                 f' --auth-mode login')
        return response.results

    def upload_datalake_directory(self, directory_source: StorageDatalakeSource):
        response = self._execute(f'fs directory upload --file-system {directory_source.container_name}'
                                 f' --source {directory_source.local_path}'
                                 f' --account-name {directory_source.storage_account_name}'
                                 f' --recursive')
        return response.results

    def create_datalake_directory(self, directory_source: StorageDatalakeSource):
        response = self._execute(f'fs directory create --file-system {directory_source.container_name}'
                                 f' --name {directory_source.local_path}'
                                 f' --account-name {directory_source.storage_account_name}'
                                 f' --auth-mode login')
        return response.results

    def set_datalake_container_acl(self, datalake_container: StorageContainer, object_id: str,
                                   permissions: str = 'r', path: str = '"/"'):
        """
        Non recursively sets datalake container acls
        :param datalake_container: The container information where the acls will be set
        :param object_id: Id of the object to be added to the access control list
        :param permissions: r, w and x permissions to be applied for the object id
        :param path: path to where the acls should be applied in the filesystem
        :return: Return of the cli command
        """
        response = self._execute(f'fs access set'
                                 f' --acl "user:{object_id}:{permissions}" --path {path}'
                                 f' --file-system {datalake_container.container_name}'
                                 f' --account-name {datalake_container.storage_account_name}'
                                 f' --account-key {datalake_container.account_key}')
        return response.results

    def update_datalake_container_acl(self, datalake_container: StorageContainer, object_id: str,
                                      permissions: str = 'r', path: str = '"/"'):
        """
        Recursively updates datalake container acls
        :param datalake_container: The container information where the acls will be set
        :param object_id: Id of the object to be added to the access control list
        :param permissions: r, w and x permissions to be applied for the object id
        :param path: path to where the acls should be applied in the filesystem
        :return: Return of the cli command
        """
        response = self._execute(f'fs access update-recursive'
                                 f' --acl "user:{object_id}:{permissions}" --path {path}'
                                 f' --file-system {datalake_container.container_name}'
                                 f' --account-name {datalake_container.storage_account_name}'
                                 f' --account-key {datalake_container.account_key}')
        return response.results

    def remove_datalake_container_acl(self, datalake_container: StorageContainer, object_id: str,
                                      path: str = '"/"'):
        """
        Recursively removes datalake container acls
        :param datalake_container: The container information where the acls will be removed
        :param object_id: Id of the object to be removed from the access control list
        :param path: path to where the acls should be removed from the filesystem
        :return: Return of the cli command
        """
        response = self._execute(f'fs access remove-recursive'
                                 f' --acl "user:{object_id}" --path {path}'
                                 f' --file-system {datalake_container.container_name}'
                                 f' --account-name {datalake_container.storage_account_name}'
                                 f' --account-key {datalake_container.account_key}')
        return response.results

    def get_storage_account_key(self, storage_account_name: str) -> str:
        response = self._execute(f'account keys list --account-name {storage_account_name}')
        key = response.results[0]['value']
        return key

    def add_ip_network_rule(self, storage_ip_network_rule: StorageIPNetworkRule):
        response = self._execute(f'account network-rule add'
                                 f' --resource-group {storage_ip_network_rule.resource_group_name}'
                                 f' --account-name {storage_ip_network_rule.storage_account_name}'
                                 f' --ip-address {storage_ip_network_rule.firewall_rule_cidr.cidr_ip_range}')

        return response

    def remove_ip_network_rule(self, storage_ip_network_rule: StorageIPNetworkRule):
        response = self._execute(f'account network-rule remove'
                                 f' --resource-group {storage_ip_network_rule.resource_group_name}'
                                 f' --account-name {storage_ip_network_rule.storage_account_name}'
                                 f' --ip-address {storage_ip_network_rule.firewall_rule_cidr.cidr_ip_range}')

        return response

    def add_vnet_network_rule(self, storage_vnet_network_rule: StorageVnetIPNetworkRule):
        if storage_vnet_network_rule.vnet_name is None:
            response = self._execute(f'account network-rule add'
                                     f' --resource-group {storage_vnet_network_rule.resource_group_name}'
                                     f' --account-name {storage_vnet_network_rule.storage_account_name}'
                                     f' --subnet {storage_vnet_network_rule.subnet}')
        else:
            response = self._execute(f'account network-rule add'
                                     f' --resource-group {storage_vnet_network_rule.resource_group_name}'
                                     f' --account-name {storage_vnet_network_rule.storage_account_name}'
                                     f' --vnet-name {storage_vnet_network_rule.vnet_name}'
                                     f' --subnet {storage_vnet_network_rule.subnet}')
        return response

    def remove_vnet_network_rule(self, storage_vnet_network_rule: StorageVnetIPNetworkRule):
        if storage_vnet_network_rule.vnet_name is None:
            response = self._execute(f'account network-rule remove'
                                     f' --resource-group {storage_vnet_network_rule.resource_group_name}'
                                     f' --account-name {storage_vnet_network_rule.storage_account_name}'
                                     f' --subnet {storage_vnet_network_rule.subnet}')
        else:
            response = self._execute(f'account network-rule remove'
                                     f' --resource-group {storage_vnet_network_rule.resource_group_name}'
                                     f' --account-name {storage_vnet_network_rule.storage_account_name}'
                                     f' --vnet-name {storage_vnet_network_rule.vnet_name}'
                                     f' --subnet {storage_vnet_network_rule.subnet}')
        return response

    def update_account_networking(self, storage_account_name: str, allow: bool):
        if allow:
            default_action = "Allow"
        else:
            default_action = "Deny"

        response = self._execute(f'account update'
                                 f' --name {storage_account_name}'
                                 f' --default-action {default_action}')

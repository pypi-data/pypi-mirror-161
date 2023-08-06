from whizbang.domain.manager.az.az_resource_manager_base import IAzResourceManager, AzResourceManagerBase
from whizbang.domain.models.az_resource_base import AzResourceGroup
from whizbang.domain.repository.az.az_resource_group_repository import IAzResourceGroupRepository
from whizbang.domain.repository.az.az_resource_repository import AzResourceRepository


class IAzResourceGroupManager(IAzResourceManager):
    """the AzResourceGroupManager interface"""

    def list_resources(self, resource: AzResourceGroup) -> list:
        raise NotImplementedError


class AzResourceGroupManager(AzResourceManagerBase, IAzResourceGroupManager):
    def __init__(self, repository: IAzResourceGroupRepository, resource_repository: AzResourceRepository):
        AzResourceManagerBase.__init__(self, repository)
        self._resource_repository = resource_repository 

    
    def list_groups(self) -> list[AzResourceGroup]:
        """Returns all the resource groups within the current subcription"""
        
        return self._repository.list()


    def list_resources(self, resource_group: AzResourceGroup) -> list:
        """Returns all the resources within the resource group
        
        :param resource_group: The group to list resources
        """
        
        return self._resource_repository.list_resources(resource_group)

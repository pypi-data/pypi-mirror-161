from whizbang.config.app_config import AppConfig
from whizbang.domain.handler.handler_base import HandlerBase
from whizbang.domain.manager.az.az_resource_group_manager import AzResourceGroupManager
from whizbang.domain.models.az_resource_base import AzResourceGroup


class ResourceGroupHandler(HandlerBase):
    """Provides methods to perform actions over Resource groups"""
    def __init__(self, app_config: AppConfig, resource_group_manager: AzResourceGroupManager):
        HandlerBase.__init__(self, app_config=app_config)
        self._resource_group_manager = resource_group_manager

    def create_resource_group(self, name: str, location: str):
        """
        Creates a new Resource Group at the current subscription.

        param name: resource group name.
        
        param location: resource group location (region).
        """

        resource_group = AzResourceGroup(
            resource_group_name=name,
            location=location
        )

        return self._resource_group_manager.create(resource_group)

    def list_groups(self) -> list[AzResourceGroup]:
        """ Returns all the resource groups within current subscription """
        return self._resource_group_manager.list_groups()
    
    def list_resources(self, resource_group_name: str) -> list:
        """
        Returns list of all the resources located at the resouce group.

        param resource_group_name: resource group name.
        """

        resource_group = AzResourceGroup(
            resource_group_name=resource_group_name
        )
        return self._resource_group_manager.list_resources( resource_group)
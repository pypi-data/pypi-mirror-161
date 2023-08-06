from abc import abstractmethod
from whizbang.data.az_cli_context import AzCliContext
from whizbang.domain.models.az_resource_base import AzResourceGroup
from whizbang.domain.repository.az.az_resource_repository_base import IAzResourceRepository, AzResourceRepositoryBase

import logging
_log = logging.getLogger(__name__) 


class IAzResourceGroupRepository(IAzResourceRepository):
    """the AzResourceGroupRepository interface"""

    @abstractmethod
    def list(self, location: str) -> list[AzResourceGroup]:
        """"""

class AzResourceGroupRepository(AzResourceRepositoryBase, IAzResourceGroupRepository):
    def __init__(self, context: AzCliContext):
        AzResourceRepositoryBase.__init__(self, context)

    @property
    def _resource_provider(self) -> str: return 'group'

    def create(self, resource: AzResourceGroup):
        """Creates a new resource group
        
        :param resource: Resource Group to be created        
        """

        if resource.location is None or resource.location == '':
            raise TypeError('Specify a location to use for the Resource Group (i.e. eastus2)')

        resource_groups = self._execute(f'list').results

        if any(rg['name'] == resource.resource_group_name for rg in resource_groups):
            _log.info(f'resource group: {resource.resource_group_name} already exists')
        else:
            return self._execute(f'create --name {resource.resource_group_name} --location {resource.location}')

    def list(self) -> list[AzResourceGroup]:  
        """Returns all the resource groups within the current subcription"""

        raw_groups = self._repository._execute(command='list').results        

        result = [AzResourceGroup(resource_group_name=group['name']) for group in raw_groups]

        return result


    
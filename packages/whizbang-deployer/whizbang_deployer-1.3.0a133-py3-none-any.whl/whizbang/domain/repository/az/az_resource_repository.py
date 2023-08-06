from xml.dom import NotSupportedErr
from whizbang.data.az_cli_context import AzCliContext
from whizbang.domain.models.az_resource_base import AzResourceGroup
from whizbang.domain.repository.az.az_repository_base import AzRepositoryBase

import logging
_log = logging.getLogger(__name__) 



class AzResourceRepository(AzRepositoryBase):
    def __init__(self, context: AzCliContext):
        AzRepositoryBase.__init__(self, context)

    @property
    def _resource_provider(self) -> str: return 'resource'    

    def list_resources(self, resource: AzResourceGroup) -> list:

        resource_group_name = resource.resource_group_name

        response = self._execute(command = f'list --resource-group {resource_group_name}')        
        
        return response.results


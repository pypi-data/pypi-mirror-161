from genericpath import exists
from whizbang.domain.manager.az.az_resource_manager_base import IAzResourceManager, AzResourceManagerBase
from whizbang.domain.models.az_resource_base import AzResourceGroup
from whizbang.domain.repository.az.az_security_repository import AzSecurityRepository
from whizbang.domain.models.defender_pricing import DefenderPricing



class AzSecurityManager(AzResourceManagerBase):
    """the AzSecurityManager class. 
    Operates over security items - mostly, Azure Defender.
    """

    def __init__(self, repository: AzSecurityRepository):
        AzResourceManagerBase.__init__(self, repository)
    
    def pricing_create(self, pricings: list[DefenderPricing]):
        """
        Creates Azure Defender pricing plans at the current subscription

        param pricings: Pricing plans to be created.
        """
        already_created = self._repository.pricing_list()

        # exclude already existing
        predicate = lambda already_created_one, creation_candidate: already_created_one.name == creation_candidate.name and already_created_one.pricing_tier == creation_candidate.pricing_tier      
        pricings_to_create = [pricing for pricing in pricings if not any([predicate(created, pricing) for created in already_created])]

        self._repository.pricing_create(pricings = pricings_to_create)

    def pricing_list(self) -> list[DefenderPricing]:
        """Returns the list of Azure Defender pricings enabled at the current subscription"""

        return self._repository.pricing_list()        
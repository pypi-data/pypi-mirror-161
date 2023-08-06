from textwrap import dedent
from xml.dom import NotSupportedErr
from whizbang.data.az_cli_context import AzCliContext
from whizbang.domain.models.az_resource_base import AzResourceGroup
from whizbang.domain.repository.az.az_repository_base import AzRepositoryBase
from whizbang.domain.models.defender_pricing import DefenderPricing

import logging
_log = logging.getLogger(__name__) 



class AzSecurityRepository(AzRepositoryBase):
    """Operates over Azure Security items (mostly Defender-related ones)"""
    def __init__(self, context: AzCliContext):
        AzRepositoryBase.__init__(self, context)

    @property
    def _resource_provider(self) -> str: return 'security'

    def create(self):
        """ Method is overriden to throw an error because security resource cannot be creted as-is.
        Need just to block the base method.
        """
        raise NotImplementedError

    def pricing_create(self, pricings: list[DefenderPricing]):
        """
        Creates the list of Azure Defender plans at the current subscription.

        param pricings: Azure Defender pricings to be created.
        """

        for pricing in pricings:
            command = f'pricing create -n {pricing.name} --tier \'{pricing.pricing_tier}\''
            self._execute(command=command)        

    def pricing_list(self) -> list[DefenderPricing]:
        """Returns Azure Defender active plans."""

        command = f'pricing list'
        pricings = self._execute(command=command).results['value']

        result = [DefenderPricing(name=pricing['name'], id = pricing['id'], pricing_tier = pricing['pricingTier']) for pricing in pricings]

        return result
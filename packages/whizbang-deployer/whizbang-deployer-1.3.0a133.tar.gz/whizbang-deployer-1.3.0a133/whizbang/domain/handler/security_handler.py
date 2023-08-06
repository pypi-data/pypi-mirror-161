from whizbang.config.app_config import AppConfig
from whizbang.config.environment_config import EnvironmentConfig
from whizbang.domain.handler.handler_base import IHandler, HandlerBase
from whizbang.domain.manager.az.az_rbac_manager import IAzRbacManager
from whizbang.domain.manager.az.az_security_manager import AzSecurityManager
from whizbang.domain.models.defender_pricing import DefenderPricing


class SecurityHandler(HandlerBase):
    """Provides methods to perform security-related setup actions"""
    def __init__(self, app_config: AppConfig,  environment_config: EnvironmentConfig, security_manager: AzSecurityManager):
        HandlerBase.__init__(self, app_config=app_config)
        self.environment_config = environment_config
        self.__security_manager = security_manager        

    def set_defender_pricings(self, pricings: list[DefenderPricing]):
        """
        Creates the list of Azure Defender plans at the current subscription.

        param pricings: Azure Defender pricings to be created.
        """
        self.__security_manager.pricing_create(pricings)
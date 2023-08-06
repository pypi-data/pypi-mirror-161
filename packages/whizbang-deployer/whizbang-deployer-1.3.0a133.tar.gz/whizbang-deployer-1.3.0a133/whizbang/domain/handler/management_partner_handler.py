from whizbang.config.app_config import AppConfig
from whizbang.domain.handler.handler_base import HandlerBase
from whizbang.domain.manager.az.az_management_partner_manager import AzManagementPartnerManager


class ManagementPartnerHandler(HandlerBase):
    def __init__(self,  app_config: AppConfig, manager: AzManagementPartnerManager):
        HandlerBase.__init__(self, app_config=app_config)
        self.manager = manager

    def get_partner_id(self):
        return self.manager.get_partner_id()

    def create_partner_id(self, partner_id: str):
        return self.manager.create_partner_id(partner_id=partner_id)

    def update_partner_id(self, partner_id: str):
        return self.manager.update_partner_id(partner_id=partner_id)

from whizbang.domain.manager.az.az_manager_base import AzManagerBase
from whizbang.domain.repository.az.az_management_partner_repository import AzManagementPartnerRepository


class AzManagementPartnerManager(AzManagerBase):
    def __init__(self, repository: AzManagementPartnerRepository):
        AzManagerBase.__init__(self, repository)

    def get_partner_id(self):
        return self._repository.get_partner_id()

    def create_partner_id(self, partner_id: str):
        return self._repository.create_partner_id(partner_id=partner_id)

    def update_partner_id(self, partner_id: str):
        return self._repository.update_partner_id(partner_id=partner_id)

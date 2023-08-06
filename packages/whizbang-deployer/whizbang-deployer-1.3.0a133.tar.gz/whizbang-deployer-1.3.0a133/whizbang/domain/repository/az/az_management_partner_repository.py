from whizbang.data.az_cli_context import AzCliContext
from whizbang.domain.repository.az.az_repository_base import AzRepositoryBase


class AzManagementPartnerRepository(AzRepositoryBase):
    def __init__(self, context: AzCliContext):
        AzRepositoryBase.__init__(self, context)

    @property
    def _resource_provider(self) -> str:
        return "managementpartner"

    def get_partner_id(self):
        response = self._execute(
            f'show')

        return response.results

    def create_partner_id(self, partner_id: str):
        response = self._execute(
            f'create --partner-id {partner_id}')

        return response.results

    def update_partner_id(self, partner_id: str):
        response = self._execute(
            f'update --partner-id {partner_id}')

        return response.results

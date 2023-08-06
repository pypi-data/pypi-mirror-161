from whizbang.domain.manager.az.az_manager_base import AzManagerBase
from whizbang.domain.repository.az.az_login_repository import AzLoginRepository


class AzLoginManager(AzManagerBase):
    def __init__(self, repository: AzLoginRepository):
        super().__init__(repository)

    def login_service_principal(self, client_id, tenant_id, key):
        return self._repository.login_service_principal(client_id, tenant_id, key)

    def login_user(self, username, tenant_id, key):
        return self._repository.login_user(username, tenant_id, key)

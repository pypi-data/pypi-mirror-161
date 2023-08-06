from whizbang.data.az_cli_context import AzCliContext
from whizbang.domain.repository.az.az_repository_base import AzRepositoryBase


class AzLoginRepository(AzRepositoryBase):
    def __init__(self, context: AzCliContext):
        AzRepositoryBase.__init__(self, context)

    @property
    def _resource_provider(self) -> str:
        return 'login'

    def login_service_principal(self, client_id, tenant_id, key):
        """
        login to azure cli as a service principal
        :param client_id: aka app id
        :param tenant_id: the tenant_id you wish to target
        :param key: service principal key
        :return:
        """

        return self._execute(f'--service-principal -u {client_id} -p {key} --tenant {tenant_id}')

    def login_user(self, username, tenant_id, key):
        """
        login to azure cli as a service principal
        :param username: e.g. john@username.com
        :param tenant_id: the tenant_id you wish to target
        :param key: service principal key
        :return:
        """

        return self._execute(f'-u {username} -p {key} --tenant {tenant_id}')

from whizbang.config.app_config import AppConfig
from whizbang.domain.handler.handler_base import HandlerBase
from whizbang.domain.manager.az.az_account_manager import AzAccountManager
from whizbang.domain.manager.az.az_login_manager import AzLoginManager
from whizbang.domain.models.active_directory.az_account import AzAccount
from whizbang.util.logger import logger


class AccountHandler(HandlerBase):
    def __init__(self, app_config: AppConfig, az_account_manager: AzAccountManager,
                 az_login_manager: AzLoginManager):
        HandlerBase.__init__(self, app_config=app_config)
        self.__az_account_manager = az_account_manager
        self.__az_login_manager = az_login_manager

    def get_account(self) -> AzAccount:
        return self.__az_account_manager.get_account()

    def switch_subscription(self, subscription_id: str):
        result = self.__az_account_manager.set_subscription(subscription_id=subscription_id)
        logger.info(result)
        return result


    def login_service_principal(self, client_id, tenant_id, key):
        """
        login to azure cli as a service principal
        :param client_id: aka app id
        :param tenant_id: the tenant_id you wish to target
        :param key: service principal key
        :return:
        """
        result = self.__az_login_manager.login_service_principal(client_id, tenant_id, key)
        logger.info(result)
        return result

    def login_user(self, username, tenant_id, key):
        """
        login to azure cli as a service principal
        :param username: e.g. john@username.com
        :param tenant_id: the tenant_id you wish to target
        :param key: service principal key
        :return:
        """
        result = self.__az_login_manager.login_user(username, tenant_id, key)
        logger.info(result)
        return result

from datetime import datetime
from time import sleep

from whizbang.domain.exceptions import AzCliRequestError
from whizbang.util import deployment_helpers
from whizbang.util.logger import logger


def wait_for_cli_action(wait_message: str, timeout_message: str, callback, timeout: int = 300, **kwargs):
    start_time = datetime.now()
    while 1:
        try:
            callback(**kwargs)
            break
        except AzCliRequestError as e:
            logger.info(deployment_helpers.timestamp(wait_message))
            sleep(10)
            time_delta = datetime.now() - start_time
            if time_delta.total_seconds() >= timeout:
                logger.error(timeout_message)
                raise e

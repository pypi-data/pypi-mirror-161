# Logging Setup
import logging


def _init_logger():
    logger = logging.getLogger(__name__)  # Create a root logger

    # Logs to be streamed
    console = logging.StreamHandler()

    # Log format
    format_str = '[%(asctime)s]\t%(levelname)s - %(processName)s %(filename)s:%(lineno)s -> %(message)s'
    console.setFormatter(logging.Formatter(format_str))

    # Print logs to the console
    logger.addHandler(console)

    # The default logging level is WARNING, so we set to DEBUG to see all logs
    logger.setLevel(logging.DEBUG)


# Setup logger
_init_logger()
logger = logging.getLogger(__name__)
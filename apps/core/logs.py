import colorlog
import logging.config
from time import sleep

class CustomFormatter(colorlog.ColoredFormatter):
    def __init__(self):
        super().__init__(
            "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )

    @staticmethod
    def log_with_delay(message, log_type="info", delay=5):
        if log_type == "info":
            logger.info(message)
        elif log_type == "warning":
            logger.warning(message)
        elif log_type == "error":
            logger.error(message)
        elif log_type == "critical":
            logger.critical(message)
        else:
            logger.debug(message)
        sleep(delay)


LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "colored": {
            "()": CustomFormatter,
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "colored",
            "level": "INFO",  # Exclude DEBUG messages
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)
log=CustomFormatter()


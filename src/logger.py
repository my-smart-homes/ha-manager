from logging import DEBUG, StreamHandler, getLogger
from sys import stdout

from colorlog import ColoredFormatter

from src.constants import FULL_DATE_FORMAT, LOG_FORMAT


def get_logger(name):

    handler = StreamHandler(stdout)
    handler.setFormatter(
        ColoredFormatter(
            fmt=LOG_FORMAT,
            datefmt=FULL_DATE_FORMAT,
        )
    )

    logger = getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(DEBUG)
    logger.propagate = False

    return logger

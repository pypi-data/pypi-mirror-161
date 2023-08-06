import logging

FORMAT = "%(asctime)s|%(name)s|%(levelname)s|%(message)s"
logger = logging.getLogger("sca-tools")
logging.basicConfig(level=logging.INFO, format=FORMAT)


def error_exit(msg):
    logger.error(msg)
    exit(1)

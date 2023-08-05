import logging

from istub.constants import LOGGER_NAME


def setup_logging(level: int = 0) -> logging.Logger:
    """
    Get Logger instance.

    Arguments:
        level -- Logging level

    Returns:
        Created Logger.
    """
    logger = logging.getLogger(LOGGER_NAME)
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s %(message)s", datefmt="%H:%M:%S")
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(level)
    logger.addHandler(stream_handler)
    logger.setLevel(level)
    return logger

import logging
import os
from pythonjsonlogger import jsonlogger

BARTERDUDE_DEFAULT_LOG_NAME = os.environ.get(
    "BARTERDUDE_DEFAULT_LOG_NAME", "barterdude"
)
BARTERDUDE_DEFAULT_LOG_LEVEL = int(
    os.environ.get(
        "BARTERDUDE_DEFAULT_LOG_LEVEL", logging.INFO
    )
)

handler = logging.StreamHandler()
handler.setFormatter(jsonlogger.JsonFormatter(
    '(levelname) (name) (pathname) (lineno)',
    timestamp=True
))
default_logger = logging.getLogger(BARTERDUDE_DEFAULT_LOG_NAME)


def getLogger(name, level=BARTERDUDE_DEFAULT_LOG_LEVEL):
    logger = default_logger.getChild(name)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger

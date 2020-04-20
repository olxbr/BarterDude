import logging
import os
from pythonjsonlogger import jsonlogger

BARTERDUDE_DEFAULT_LOG_NAME = os.environ.get(
    "BARTERDUDE_DEFAULT_LOG_NAME", "barterdude"
)

handler = logging.StreamHandler()
handler.setFormatter(jsonlogger.JsonFormatter(
    '(levelname) (name) (pathname) (lineno)',
    timestamp=True
))


def getLogger(name=BARTERDUDE_DEFAULT_LOG_NAME, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

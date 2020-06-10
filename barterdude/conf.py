import logging
import os
from pythonjsonlogger import jsonlogger

BARTERDUDE_DEFAULT_APP_NAME = os.environ.get(
    "BARTERDUDE_DEFAULT_APP_NAME", "barterdude"
)
BARTERDUDE_DEFAULT_LOG_LEVEL = int(
    os.environ.get(
        "BARTERDUDE_DEFAULT_LOG_LEVEL", logging.INFO
    )
)
BARTERDUDE_LOG_REDACTED = bool(int(os.environ.get(
    "BARTERDUDE_LOG_REDACTED", "1"
)))
handler = logging.StreamHandler()
handler.setFormatter(jsonlogger.JsonFormatter(
    '(levelname) (name) (pathname) (lineno)',
    timestamp=True
))
default_logger = logging.getLogger(BARTERDUDE_DEFAULT_APP_NAME)


def getLogger(name, level=BARTERDUDE_DEFAULT_LOG_LEVEL):
    logger = default_logger.getChild(name)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger

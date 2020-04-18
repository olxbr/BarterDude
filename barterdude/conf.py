import logging

from pythonjsonlogger import jsonlogger


def getLogger(name="barterdude", level=logging.INFO):
    handler = logging.StreamHandler()
    handler.setFormatter(jsonlogger.JsonFormatter(
        '(levelname) (name) (pathname) (lineno)',
        timestamp=True
    ))
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

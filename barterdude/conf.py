import logging

from pythonjsonlogger import jsonlogger


handler = logging.StreamHandler()
handler.setFormatter(jsonlogger.JsonFormatter(
    '(levelname) (name) (pathname) (lineno)',
    timestamp=True
))
logger = logging.getLogger('barterdude')
logger.addHandler(handler)

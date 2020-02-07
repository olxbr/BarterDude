from barterdude.hooks import BaseHook
import logging


class Logging(BaseHook):
    async def before_consume(self, message):
        logging.info(f"going to consume message: {message}")

    async def on_success(self, message):
        logging.info(f"successfully consumed message: {message}")

    async def on_fail(self, message, error):
        logging.error(f"failed to consume message ({error}): {message}")

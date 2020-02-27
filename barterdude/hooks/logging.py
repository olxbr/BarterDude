from logging import getLogger
from traceback import format_tb
from barterdude.hooks import BaseHook
from asyncworker.rabbitmq.message import RabbitMQMessage


class Logging(BaseHook):
    def __init__(self):
        self.__logger = getLogger('barterdude')

    async def before_consume(self, message: RabbitMQMessage):
        self.__logger.info(f"going to consume message: {message.body}")

    async def on_success(self, message: RabbitMQMessage):
        self.__logger.info(f"successfully consumed message: {message.body}")

    async def on_fail(self, message: RabbitMQMessage, error: Exception):
        tb = format_tb(error.__traceback__)
        self.__logger.error(
            f"failed to consume message: {message.body}\n{repr(error)}\n{tb}"
        )

from barterdude.hooks import BaseHook
from asyncworker.rabbitmq.message import RabbitMQMessage


class ErrorHook(BaseHook):
    async def on_success(self, message: RabbitMQMessage):
        raise NotImplementedError

    async def on_fail(self, message: RabbitMQMessage, error: Exception):
        raise NotImplementedError

    async def before_consume(self, message: RabbitMQMessage):
        raise NotImplementedError

    async def on_connection_fail(self, error: Exception, retries: int):
        raise NotImplementedError

import json
from traceback import format_tb
from logging import INFO
from asyncworker.rabbitmq.message import RabbitMQMessage

from barterdude.conf import getLogger
from barterdude.hooks import BaseHook


class Logging(BaseHook):

    def __init__(self, name="barterdude", level=INFO):
        self._logger = getLogger(name, level)

    @property
    def logger(self):
        return self._logger

    async def before_consume(self, message: RabbitMQMessage):
        self.logger.info({
            "message": "Before consume message",
            "delivery_tag": message._delivery_tag,
            "message_body": json.dumps(message.body),
        })

    async def on_success(self, message: RabbitMQMessage):
        self.logger.info({
            "message": "Successfully consumed message",
            "delivery_tag": message._delivery_tag,
            "message_body": json.dumps(message.body),
        })

    async def on_fail(self, message: RabbitMQMessage, error: Exception):
        self.logger.error({
            "message": "Failed to consume message",
            "delivery_tag": message._delivery_tag,
            "message_body": json.dumps(message.body),
            "exception": repr(error),
            "traceback": format_tb(error.__traceback__),
        })

    async def on_connection_fail(self, error: Exception, retries: int):
        self.logger.error({
            "message": "Failed to connect to the broker",
            "retries": retries,
            "exception": repr(error),
            "traceback": format_tb(error.__traceback__),
        })

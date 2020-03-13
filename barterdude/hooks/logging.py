import json
from traceback import format_tb

from asyncworker.rabbitmq.message import RabbitMQMessage

from barterdude.conf import logger
from barterdude.hooks import BaseHook


class Logging(BaseHook):
    async def before_consume(self, message: RabbitMQMessage):
        logger.info({
            "message": "Before consume message",
            "delivery_tag": message._delivery_tag,
            "message_body": json.dumps(message.body),
        })

    async def on_success(self, message: RabbitMQMessage):
        logger.info({
            "message": "Successfully consumed message",
            "delivery_tag": message._delivery_tag,
            "message_body": json.dumps(message.body),
        })

    async def on_fail(self, message: RabbitMQMessage, error: Exception):
        logger.error({
            "message": "Failed to consume message",
            "delivery_tag": message._delivery_tag,
            "message_body": json.dumps(message.body),
            "exception": repr(error),
            "traceback": format_tb(error.__traceback__),
        })

    async def on_connection_fail(self, error: Exception, retries: int):
        logger.error({
            "message": "Failed to connect to the broker",
            "retries": retries,
            "exception": repr(error),
            "traceback": format_tb(error.__traceback__),
        })

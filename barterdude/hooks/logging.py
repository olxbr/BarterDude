import json
from traceback import format_tb
from asyncworker.rabbitmq.message import RabbitMQMessage

from barterdude.conf import (
    getLogger,
    BARTERDUDE_DEFAULT_LOG_LEVEL,
    BARTERDUDE_LOG_REDACTED
)
from barterdude.hooks import BaseHook


class Logging(BaseHook):

    def __init__(
        self, name="hook.logging",
        level=BARTERDUDE_DEFAULT_LOG_LEVEL
    ):
        self._logger = getLogger(name, level)

    @property
    def logger(self):
        return self._logger

    def _add_message_body(
            self, log_message: dict, message: RabbitMQMessage) -> dict:
        if not BARTERDUDE_LOG_REDACTED:
            log_message["message_body"] = json.dumps(message.body)
        return log_message

    async def before_consume(self, message: RabbitMQMessage):
        self.logger.info(
            self._add_message_body({
                "message": "Before consume message",
                "delivery_tag": message._delivery_tag,
            }, message)
        )

    async def on_success(self, message: RabbitMQMessage):
        self.logger.info(
            self._add_message_body({
                "message": "Successfully consumed message",
                "delivery_tag": message._delivery_tag,
            }, message)
        )

    async def on_fail(self, message: RabbitMQMessage, error: Exception):
        self.logger.error(
            self._add_message_body({
                "message": "Failed to consume message",
                "delivery_tag": message._delivery_tag,
                "exception": repr(error),
                "traceback": format_tb(error.__traceback__),
            }, message)
        )

    async def on_connection_fail(self, error: Exception, retries: int):
        self.logger.error({
            "message": "Failed to connect to the broker",
            "retries": retries,
            "exception": repr(error),
            "traceback": format_tb(error.__traceback__),
        })

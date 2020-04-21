from traceback import format_tb
from typing import Iterable, Callable, Optional, Any

from asyncio import gather
from asyncworker.rabbitmq.message import RabbitMQMessage

from barterdude.conf import getLogger, BARTERDUDE_DEFAULT_LOG_LEVEL


class Monitor:
    def __init__(self, *hooks: Iterable):
        self.__hooks = hooks
        self._logger = getLogger(
            "hook.monitor", BARTERDUDE_DEFAULT_LOG_LEVEL)

    async def _callback(self,
                        method: Callable[[RabbitMQMessage], Optional[Any]],
                        message: RabbitMQMessage,
                        error: Optional[Exception] = None):
        try:
            return await (method(message, error) if error else method(message))
        except Exception as e:
            self._logger.error({
                "message": f"Error on hook method {method}",
                "exception": repr(e),
                "traceback": format_tb(e.__traceback__),
            })

    def _prepare_callbacks(self, method_name: str,
                           message: RabbitMQMessage,
                           error: Optional[Exception] = None):
        callbacks = []
        for hook in self.__hooks:
            callbacks.append(
                self._callback(getattr(hook, method_name), message, error)
            )
        return callbacks

    async def dispatch_before_consume(self, message: RabbitMQMessage):
        await gather(*self._prepare_callbacks("before_consume", message))

    async def dispatch_on_success(self, message: RabbitMQMessage):
        await gather(*self._prepare_callbacks("on_success", message))

    async def dispatch_on_fail(self, message: RabbitMQMessage,
                               error: Exception):
        await gather(*self._prepare_callbacks("on_fail", message, error))

    async def dispatch_on_connection_fail(
            self, error: Exception, retries: int
    ):
        await gather(*self._prepare_callbacks(
            "on_connection_fail", error, retries
        ))

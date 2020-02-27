from logging import getLogger
from asyncio import gather
from asyncworker.rabbitmq.message import RabbitMQMessage
from typing import Iterable, Callable, Optional, Any


class Monitor:
    def __init__(self, *hooks: Iterable):
        self.__hooks = hooks
        self.__logger = getLogger('barterdude')

    async def _callback(self,
                        method: Callable[[RabbitMQMessage], Optional[Any]],
                        message: RabbitMQMessage,
                        error: Optional[Exception] = None):
        try:
            return await (method(message, error) if error else method(message))
        except Exception as e:
            self.__logger.warning(f"Error on hook method {method}: %s", e)

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

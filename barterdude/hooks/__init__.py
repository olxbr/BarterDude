from aiohttp import web
from abc import ABCMeta, abstractmethod
from barterdude import BarterDude
from asyncworker.rabbitmq.message import RabbitMQMessage


class BaseHook(metaclass=ABCMeta):
    @abstractmethod
    async def on_success(self, message: RabbitMQMessage):
        '''Called after successfuly consumed the message'''

    @abstractmethod
    async def on_fail(self, message: RabbitMQMessage, error: Exception):
        '''Called when fails to consume the message'''

    @abstractmethod
    async def before_consume(self, message: RabbitMQMessage):
        '''Called before consuming the message'''

    @abstractmethod
    async def on_connection_fail(self, error: Exception, retries: int):
        '''Called when the consumer fails to connect to the broker'''


class HttpHook(BaseHook):
    def __init__(self, barterdude: BarterDude, path: str):
        barterdude.add_endpoint(
            routes=[path],
            methods=["GET"],
            hook=self.__call__
        )

    async def __call__(self, req: web.Request):
        raise NotImplementedError

    async def on_success(self, message: RabbitMQMessage):
        raise NotImplementedError

    async def on_fail(self, message: RabbitMQMessage, error: Exception):
        raise NotImplementedError

    async def before_consume(self, message: RabbitMQMessage):
        raise NotImplementedError

    async def on_connection_fail(self, error: Exception, retries: int):
        raise NotImplementedError

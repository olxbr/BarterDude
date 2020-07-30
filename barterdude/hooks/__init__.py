from aiohttp import web
from abc import ABCMeta
from barterdude import BarterDude
from barterdude.message import Message


class BaseHook(metaclass=ABCMeta):
    async def on_success(self, message: Message):
        '''Called after successfuly consumed the message'''
        pass

    async def on_fail(self, message: Message, error: Exception):
        '''Called when fails to consume the message'''
        pass

    async def before_consume(self, message: Message):
        '''Called before consuming the message'''
        pass

    async def on_connection_fail(self, error: Exception, retries: int):
        '''Called when the consumer fails to connect to the broker'''
        pass


class HttpHook(BaseHook):
    def __init__(self, barterdude: BarterDude, path: str):
        barterdude.add_endpoint(
            routes=[path],
            methods=["GET"],
            hook=self.__call__
        )

    async def __call__(self, req: web.Request):
        raise NotImplementedError()

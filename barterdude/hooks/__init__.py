from abc import ABCMeta, abstractmethod
from barterdude import BarterDude


class BaseHook(metaclass=ABCMeta):
    @abstractmethod
    async def on_success(self, message: dict):
        '''Called after successfuly consumed the message'''

    @abstractmethod
    async def on_fail(self, message: dict, error: Exception):
        '''Called when fails to consume the message'''

    @abstractmethod
    async def before_consume(self, message: dict):
        '''Called before consuming the message'''


class HttpHook(BaseHook):
    def __init__(self, barterdude: BarterDude, path: str):
        barterdude.add_endpoint(
            routes=[path],
            methods=["GET"],
            hook=self
        )

    async def __call__(self, *args, **kwargs):
        raise NotImplementedError

    async def on_success(self, message):
        raise NotImplementedError

    async def on_fail(self, message, error):
        raise NotImplementedError

    async def before_consume(self, message):
        raise NotImplementedError

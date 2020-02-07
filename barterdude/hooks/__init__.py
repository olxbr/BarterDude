from abc import ABCMeta, abstractmethod
from asyncworker import RouteTypes


class BaseHook(metaclass=ABCMeta):
    @abstractmethod
    async def on_success(self, message):
        '''Called after successfuly consumed the message'''

    @abstractmethod
    async def on_fail(self, message, error):
        '''Called when fails to consume the message'''

    @abstractmethod
    async def before_consume(self, message):
        '''Called before consuming the message'''


class HttpHook(BaseHook):
    def __init__(self, baterdude, path: str):
        self.__barterdude = baterdude
        self.__path = path

        self._start_server()

    def _start_server(self):
        self.__barterdude.route(
            routes=[self.__path],
            methods=["GET"],
            type=RouteTypes.HTTP
        )(self)

    async def __call__(self, *args, **kwargs):
        raise NotImplementedError

    async def on_success(self, message):
        raise NotImplementedError

    async def on_fail(self, message, error):
        raise NotImplementedError

    async def before_consume(self, message):
        raise NotImplementedError

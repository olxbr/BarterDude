from abc import ABC
from asyncworker import RouteTypes


class BaseHook(ABC):
    async def on_success(self, message):
        return NotImplemented

    async def on_fail(self, message):
        return NotImplemented

    async def before_consume(self, message):
        return NotImplemented


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
        return NotImplemented

import threading

from barterdude import BarterDude
from barterdude.hooks import HttpHook
from aiohttp import web


class Healthcheck(HttpHook):
    def __init__(
        self,
        barterdude: BarterDude,
        path: str = "/healthcheck",
        error_rate: float = 0.05,
        clear_seconds: int = 10
    ):
        self.__error_rate = error_rate
        self.__clear_seconds = clear_seconds
        self._clear_rates()
        super(Healthcheck, self).__init__(barterdude, path)

    def _clear_rates(self):
        self.__success = self.__error = 0
        timer = threading.Timer(self.__clear_seconds, self._clear_rates)
        timer.daemon = True
        timer.start()

    async def on_success(self, message):
        self.__success += 1

    async def on_fail(self, message, error):
        self.__error += 1

    async def __call__(self, *args, **kwargs):
        if self.__success:
            rate = self.__error/(self.__success + self.__error)
            if rate >= self.__error_rate:
                return web.Response(
                    body=f"Error rate in {rate}, above {self.__error_rate}",
                    status=500
                )
        elif self.__error:
            return web.Response(
                body=f"Only error happened. {self.__error} until now",
                status=500
            )
        return web.Response(
            body=f"Bater like a dude! Error rate: {rate}",
            status=200
        )

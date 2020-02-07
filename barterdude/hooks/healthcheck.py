from barterdude import BarterDude
from barterdude.hooks import HttpHook
from aiohttp import web
from time import time
from collections import deque
from bisect import bisect_left


def _remove_old(instants: deque, old_timestamp: float):
    pos = bisect_left(instants, old_timestamp)
    for i in range(0, pos):
        instants.popleft()
    return len(instants)


class Healthcheck(HttpHook):
    def __init__(
        self,
        barterdude: BarterDude,
        path: str = "/healthcheck",
        success_rate: float = 0.95,
        health_window: float = 60.0  # seconds
    ):
        self.__success_rate = success_rate
        self.__health_window = health_window
        self.__success = deque()
        self.__fail = deque()
        self.__force_fail = False
        super(Healthcheck, self).__init__(barterdude, path)

    def force_fail(self):
        self.__force_fail = True

    async def on_success(self, message):
        self.__success.append(time())

    async def on_fail(self, message, error):
        self.__fail.append(time())

    async def __call__(self, *args, **kwargs):
        if self.__force_fail:
            return web.Response(
                body="Healthcheck fail called manually",
                status=500
            )
        old_timestamp = time() - self.__health_window
        success = _remove_old(self.__success, old_timestamp)
        fail = _remove_old(self.__fail, old_timestamp)
        if success == 0 and fail == 0:
            return web.Response(
                body="No messages until now",
                status=200
            )
        rate = success / (success + fail)
        if rate >= self.__success_rate:
            return web.Response(
                body=f"Bater like a pro! Success rate: {rate}",
                status=200
            )
        else:
            return web.Response(
                body=f"Success rate {rate} bellow {self.__success_rate}",
                status=500
            )

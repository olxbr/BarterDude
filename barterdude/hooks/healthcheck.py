from abc import ABC, abstractmethod
import json

from barterdude import BarterDude
from barterdude.hooks import HttpHook
from asyncworker.rabbitmq.message import RabbitMQMessage
from aiohttp import web
from time import time
from collections import deque
from bisect import bisect_left


def _remove_old(instants: deque, old_timestamp: float):
    pos = bisect_left(instants, old_timestamp)
    for i in range(0, pos):
        instants.popleft()
    return len(instants)


def _response(status, body):
    body["status"] = "ok" if status == 200 else "fail"
    return web.Response(status=status, body=json.dumps(body))


class HealthcheckMonitored(ABC):
    @abstractmethod
    def healthcheck(self):
        pass


class Healthcheck(HttpHook):
    def __init__(
        self,
        barterdude: BarterDude,
        path: str = "/healthcheck",
        success_rate: float = 0.95,
        health_window: float = 60.0,  # seconds
        max_connection_fails: int = 3
    ):
        self.__barterdude = barterdude
        self.__success_rate = success_rate
        self.__health_window = health_window
        self.__success = deque()
        self.__fail = deque()
        self.__force_fail = False
        self.__connection_fails = 0
        self.__max_connection_fails = max_connection_fails
        super(Healthcheck, self).__init__(barterdude, path)

    def force_fail(self):
        self.__force_fail = True

    async def before_consume(self, message: RabbitMQMessage):
        pass

    async def on_success(self, message: RabbitMQMessage):
        self.__success.append(time())

    async def on_fail(self, message: RabbitMQMessage, error: Exception):
        self.__fail.append(time())

    async def on_connection_fail(self, error: Exception, retries: int):
        self.__connection_fails = retries

    async def __call__(self, req: web.Request):
        if self.__force_fail:
            return _response(500, {
                "message": "Healthcheck fail called manually"
            })

        if self.__connection_fails >= self.__max_connection_fails:
            return _response(500, {
                "message": (
                    "Reached max connection fails "
                    f"({self.__max_connection_fails})"
                )
            })

        response = {}
        status = 200

        all_monitored_modules_passed = True
        for module in self.__barterdude:
            if isinstance(self.__barterdude[module], HealthcheckMonitored):
                passed = self.__barterdude[module].healthcheck()
                response[module] = "ok" if passed else "fail"
                all_monitored_modules_passed &= passed

        if not all_monitored_modules_passed:
            status = 500

        old_timestamp = time() - self.__health_window
        success = _remove_old(self.__success, old_timestamp)
        fail = _remove_old(self.__fail, old_timestamp)

        if success == 0 and fail == 0:
            response["message"] = (
                f"No messages in last {self.__health_window}s"
            )
            return _response(status, response)

        rate = success / (success + fail)

        if rate < self.__success_rate:
            status = 500

        response.update({
            "message":
                f"Success rate: {rate} (expected: {self.__success_rate})",
            "fail": fail,
            "success": success
        })

        return _response(status, response)

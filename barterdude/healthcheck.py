from barterdude import BarterDude
from asyncworker import RouteTypes
from aiohttp import web


class Healthcheck:
    def __init__(
        self,
        barterdude: BarterDude,
        path: str = "/healthcheck",
        errors_rate: float = 0.05
    ):
        self.__barterdude = barterdude
        self.__path = path
        self.__success = self.__error = 0
        self.__error_rate = errors_rate

    def incr_success(self):
        self.__success += 1

    def incr_error(self):
        self.__error += 1

    def start_monitor(self):
        self.__barterdude.route(
            routes=[self.__path],
            methods=["GET"],
            type=RouteTypes.HTTP
        )(self)

    def __call__(self, *args, **kwargs):
        if self.__success:
            rate = self.__error/self.__success
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

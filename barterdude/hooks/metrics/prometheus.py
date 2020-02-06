from aiohttp import web

from barterdude import BarterDude
from barterdude.hooks import HttpHook

try:
    from prometheus_client import CollectorRegistry, generate_latest
except ImportError:
    print("""
    Please install extra dependency with:
        `pip install barterdude[prometheus]`
    """)


class Prometheus(HttpHook):
    def __init__(
        self,
        barterdude: BarterDude,
        path: str = "/metrics",
        registry: CollectorRegistry = CollectorRegistry()
    ):
        self.__registry = registry
        super(Prometheus, self).__init__(barterdude, path)

    async def before_consume(self, message):
        pass

    async def on_success(self, message):
        pass

    async def on_fail(self, message, error):
        pass

    async def __call__(self, *args, **kwargs):
        return web.Response(
            body=generate_latest(self.__registry),
            status=200
        )

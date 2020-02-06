from aiohttp import web

from barterdude import BarterDude
from barterdude.hooks import HttpHook

try:
    from prometheus_client import (
        CollectorRegistry,
        generate_latest,
        Counter,
        CONTENT_TYPE_LATEST
    )
except ImportError:
    print("""
    Please install extra dependency with:
        `pip install barterdude[prometheus]`
    """)


class Prometheus(HttpHook):
    def __init__(
        self,
        barterdude: BarterDude,
        labels: dict,
        path: str = "/metrics",
        registry: CollectorRegistry = CollectorRegistry()
    ):
        self.__registry = registry
        self.__labelnames = list(labels.keys())
        self.__labelvalues = list(labels.values())
        self.__namespace = "barterdude"
        self.__unit = "messages"
        self.__prepare_metrics()
        super(Prometheus, self).__init__(barterdude, path)

    def __prepare_before_consume(self, default_kwargs):
        self.__before_consume_gauge = Counter(
            name="received_number_before_consume",
            documentation="Messages that worker received from queue(s)",
            **default_kwargs
        )

    def __prepare_on_success(self, default_kwargs):
        self.__on_success_gauge = Counter(
            name="consumed_number_on_success",
            documentation=("Messages that worker consumed with success"
                           " from queue(s)"),
            **default_kwargs
        )

    def __prepare_on_fail(self, default_kwargs):
        default_kwargs["labelnames"] += ["error"]
        self.__on_fail_gauge = Counter(
            name="consumed_number_on_fail",
            documentation=("Messages that worker consumed with fail"
                           "from queue(s)"),
            **default_kwargs
        )

    def __prepare_metrics(self):
        default_kwargs = dict(
            labelnames=self.__labelnames,
            namespace=self.__namespace,
            unit=self.__unit,
        )
        self.__prepare_before_consume(default_kwargs)
        self.__prepare_on_success(default_kwargs)
        self.__prepare_on_fail(default_kwargs)

    async def before_consume(self, message):
        self.__before_consume_gauge.labels(**self.__labelvalues).inc()

    async def on_success(self, message):
        self.__on_success_gauge.labels(**self.__labelvalues).inc()

    async def on_fail(self, message, error):
        self.__on_fail_gauge.labels(
            error=str(type(error)), **self.__labelvalues
        ).inc()

    async def __call__(self, *args, **kwargs):
        return web.Response(
            content_type=CONTENT_TYPE_LATEST.split(";")[0],
            charset=CONTENT_TYPE_LATEST.split("=")[-1],
            body=generate_latest(self.__registry),
            status=200,
        )

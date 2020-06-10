import time
from aiohttp import web
from typing import Optional
from asyncworker.rabbitmq.message import RabbitMQMessage
from barterdude import BarterDude
from barterdude.hooks import HttpHook
from barterdude.hooks.metrics.prometheus.definitions import Definitions
from barterdude.hooks.metrics.prometheus.metrics import Metrics
try:
    from prometheus_client import (
        CollectorRegistry,
        generate_latest,
        CONTENT_TYPE_LATEST,
    )
except ImportError:  # pragma: no cover
    raise ImportError("""
    Please install extra dependency with:
        `pip install barterdude[prometheus]`
    """)


class Prometheus(HttpHook):

    def __init__(
        self,
        barterdude: BarterDude,
        labels: dict = {},
        path: str = "/metrics",
        registry: CollectorRegistry = None
    ):
        self.__registry = registry or CollectorRegistry()
        self.__labels = labels
        self.__metrics = Metrics(self.__registry)
        self.__definitions = Definitions(
            self.__registry, self.__metrics, list(self.__labels.keys())
        )
        self._msg_start = {}
        self.__definitions.save_metrics()
        super(Prometheus, self).__init__(barterdude, path)

    @property
    def metrics(self):
        return self.__metrics

    async def before_consume(self, message: RabbitMQMessage):
        hash_message = id(message)
        self._msg_start[hash_message] = time.time()
        metric = self.metrics[self.__definitions.BEFORE_CONSUME]
        if self.__labels:
            metric = metric.labels(**self.__labels)
        metric.inc()

    async def _on_complete(self,
                           message: RabbitMQMessage,
                           state: str,
                           error: Optional[Exception] = None):

        final_time = time.time()
        hash_message = id(message)
        labels = self.__labels.copy()
        labels["state"] = state
        labels["error"] = str(type(error)) if error else ""
        self.metrics[self.__definitions.HISTOGRAM_MEASURE].labels(
            **labels).observe(
                final_time - self._msg_start.pop(hash_message)
        )

    async def on_success(self, message: RabbitMQMessage):
        await self._on_complete(message, self.__definitions.SUCCESS)

    async def on_fail(self, message: RabbitMQMessage, error: Exception):
        await self._on_complete(message, self.__definitions.FAIL, error)

    async def on_connection_fail(self, error: Exception, retries: int):
        metric = self.metrics[self.__definitions.CONNECTION_FAIL]
        if self.__labels:
            metric = metric.labels(**self.__labels)
        metric.inc()

    async def __call__(self, req: web.Request):
        return web.Response(
            content_type=CONTENT_TYPE_LATEST.split(";")[0],
            charset=CONTENT_TYPE_LATEST.split("=")[-1],
            body=generate_latest(self.__registry),
            status=200,
        )

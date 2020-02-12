import time
from aiohttp import web
from typing import Optional

from barterdude import BarterDude
from barterdude.hooks import HttpHook
from barterdude.hooks.metrics.prometheus.definition import Definition

try:
    from prometheus_client import (
        CollectorRegistry,
        generate_latest,
        CONTENT_TYPE_LATEST
    )
except ImportError:
    raise ImportError("""
    Please install extra dependency with:
        `pip install barterdude[prometheus]`
    """)


class Prometheus(HttpHook):

    MESSAGE_UNITS = "messages"
    TIME_UNITS = "seconds"
    NAMESPACE = "barterdude"
    D_BEFORE_CONSUME = "before_consume"
    D_SUCCESS = "success"
    D_FAIL = "fail"
    D_TIME_MEASURE = "time_measure"

    def __init__(
        self,
        barterdude: BarterDude,
        labels: dict,
        path: str = "/metrics",
        registry: CollectorRegistry = CollectorRegistry(),
        definition: Definition = Definition()
    ):
        self.__registry = registry
        self.__labels = labels
        self._d = definition
        self._msg_start = {}
        self.__prepare_metrics()
        super(Prometheus, self).__init__(barterdude, path)

    def __prepare_metrics(self):
        self._d.prepare_before_consume(
            self.D_BEFORE_CONSUME,
            labelnames=list(self.__labels.keys()),
            namespace=self.NAMESPACE,
            unit=self.MESSAGE_UNITS,
            registry=self.__registry
        )
        self._d.prepare_on_complete(
            self.D_SUCCESS,
            labelnames=list(self.__labels.keys()),
            namespace=self.NAMESPACE,
            unit=self.MESSAGE_UNITS,
            registry=self.__registry
        )
        self._d.prepare_on_complete(
            self.D_FAIL,
            labelnames=list(self.__labels.keys()),
            namespace=self.NAMESPACE,
            unit=self.MESSAGE_UNITS,
            registry=self.__registry
        )
        self._d.prepare_time_measure(
            self.D_TIME_MEASURE,
            labelnames=list(self.__labels.keys()),
            namespace=self.NAMESPACE,
            unit=self.TIME_UNITS,
            registry=self.__registry
        )

    async def before_consume(self, message: dict):
        hash_message = id(message)
        self._d.metrics[self.D_BEFORE_CONSUME].labels(
            **self.__labels
        ).inc()
        self._msg_start[hash_message] = time.time()

    async def _on_complete(self,
                           message: dict,
                           state: str,
                           error: Optional[Exception] = None):

        final_time = time.time()
        hash_message = id(message)
        labels = self.__labels.copy()
        labels["state"] = state
        labels["error"] = str(type(error)) if (error) else None
        self._d.metrics[state].labels(**labels).inc()
        self._d.metrics[self.D_TIME_MEASURE].labels(**labels).observe(
            final_time - self._msg_start.pop(hash_message)
        )

    async def on_success(self, message: dict):
        await self._on_complete(message, self.D_SUCCESS)

    async def on_fail(self, message: dict, error: Exception):
        await self._on_complete(message, self.D_FAIL, error)

    async def __call__(self, *args, **kwargs):
        return web.Response(
            content_type=CONTENT_TYPE_LATEST.split(";")[0],
            charset=CONTENT_TYPE_LATEST.split("=")[-1],
            body=generate_latest(self.__registry),
            status=200,
        )

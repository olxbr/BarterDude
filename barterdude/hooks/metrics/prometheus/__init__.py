import time
import copy
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
    print("""
    Please install extra dependency with:
        `pip install barterdude[prometheus]`
    """)


class Prometheus(HttpHook):

    MESSAGE_UNITS = "messages"
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
        self.__labelnames = list(labels.keys())
        self.__labelvalues = list(labels.values())
        self._d = definition
        self._time_bucket = {}
        self.__prepare_metrics()
        super(Prometheus, self).__init__(barterdude, path)

    def __prepare_metrics(self):
        default_kwargs = dict(
            labelnames=self.__labelnames,
            namespace=self.NAMESPACE,
            unit=self.MESSAGE_UNITS,
            registry=self.__registry
        )
        self._d.prepare_before_consume(
            self.D_BEFORE_CONSUME, copy.deepcopy(default_kwargs)
        )
        self._d.prepare_on_complete(
            self.D_SUCCESS, copy.deepcopy(default_kwargs)
        )
        self._d.prepare_on_complete(self.D_FAIL, copy.deepcopy(default_kwargs))
        self._d.prepare_time_measure(
            self.D_TIME_MEASURE, copy.deepcopy(default_kwargs)
        )

    async def __compute_hash(self, message: dict):
        return id(message)

    async def before_consume(self, message: dict):
        hash_message = await self.__compute_hash(message)
        self._d.senders[self.D_BEFORE_CONSUME].labels(
            **self.__labels
        ).inc()
        self._time_bucket[hash_message] = time.time()

    async def _on_complete(self,
                           message: dict,
                           state: str,
                           error: Optional[Exception] = None):

        final_time = time.time()
        hash_message = await self.__compute_hash(message)
        labels = self.__labels.copy()
        labels["state"] = state
        labels["error"] = str(type(error)) if (error) else None
        self._d.senders[state].labels(**labels).inc()
        start_time = self._time_bucket.get(hash_message)
        self._d.senders[self.D_TIME_MEASURE].labels(**labels).observe(
            final_time - start_time
        )
        del self._time_bucket[hash_message]

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

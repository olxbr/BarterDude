try:
    from prometheus_client import (
        CollectorRegistry,
        Counter,
        Histogram
    )
except ImportError:
    raise ImportError("""
    Please install extra dependency with:
        `pip install barterdude[prometheus]`
    """)
from typing import Iterable
from barterdude.hooks.metrics.prometheus.metrics import Metrics


class Definition:

    def __init__(
        self,
        histogram_buckets: tuple = Histogram.DEFAULT_BUCKETS,
        metrics: Metrics = Metrics()
    ):
        self.__histogram_buckets = histogram_buckets
        self.__metrics = metrics

    @property
    def metrics(self):
        return self.__metrics

    def prepare_before_consume(
            self, name: str, labelnames: Iterable[str] = (),
            namespace: str = "", unit: str = "",
            registry: CollectorRegistry = CollectorRegistry()):

        self.metrics[name] = Counter(
                name="received_number_before_consume",
                documentation="Messages that worker received from queue(s)",
                labelnames=labelnames,
                namespace=namespace,
                unit=unit,
                registry=registry
            )

    def prepare_on_complete(
            self, state: str, labelnames: Iterable[str] = (),
            namespace: str = "", unit: str = "",
            registry: CollectorRegistry = CollectorRegistry()):

        labelnames += ["state", "error"]

        self.metrics[state] = Counter(
                name=f"consumed_number_on_{state}",
                documentation=(f"Messages that worker consumed with {state}"
                               " from queue(s)"),
                labelnames=labelnames,
                namespace=namespace,
                unit=unit,
                registry=registry
            )

    def prepare_time_measure(
            self, name: str, labelnames: Iterable[str] = (),
            namespace: str = "", unit: str = "",
            registry: CollectorRegistry = CollectorRegistry()):

        labelnames += ["state", "error"]

        self.metrics[name] = Histogram(
                name="time_spent_processing_message",
                documentation=("Time spent when function was "
                               "processing a message"),
                buckets=self.__histogram_buckets,
                labelnames=labelnames,
                namespace=namespace,
                unit=unit,
                registry=registry
            )

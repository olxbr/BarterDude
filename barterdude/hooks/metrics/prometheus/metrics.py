from prometheus_client.metrics import MetricWrapperBase
from prometheus_client import (
    Counter,
    Gauge,
    Summary,
    Histogram,
    Info,
    Enum
)
from functools import partial


class Metrics(dict):

    def __init__(self, registry):
        self.__registry = registry

    @property
    def counter(self) -> Counter.__class__:
        return partial(Counter, registry=self.__registry)

    @property
    def gauge(self) -> Gauge.__class__:
        return partial(Gauge, registry=self.__registry)

    @property
    def summary(self) -> Summary.__class__:
        return partial(Summary, registry=self.__registry)

    @property
    def histogram(self) -> Histogram.__class__:
        return partial(Histogram, registry=self.__registry)

    @property
    def info(self) -> Info.__class__:
        return partial(Info, registry=self.__registry)

    @property
    def enum(self) -> Enum.__class__:
        return partial(Enum, registry=self.__registry)

    def __setitem__(self, name: str, metric: MetricWrapperBase):
        if name in self:
            value = self.__getitem__(name)
            raise ValueError(
                f"Key {name} already exists with value {value}"
            )
        super(Metrics, self).__setitem__(name, metric)

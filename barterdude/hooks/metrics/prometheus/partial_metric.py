import functools
from prometheus_client import (
    CollectorRegistry,
)
from prometheus_client.metrics import MetricWrapperBase


def partial_metric(cls: MetricWrapperBase, registry: CollectorRegistry):

    class RegistryMetric(cls):
        __init__ = functools.partialmethod(cls.__init__, registry=registry)

    return RegistryMetric

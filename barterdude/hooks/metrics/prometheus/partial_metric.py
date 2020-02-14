import functools

try:
    from prometheus_client import (
        CollectorRegistry,
    )
    from prometheus_client.metrics import MetricWrapperBase
except ImportError:
    raise ImportError("""
    Please install extra dependency with:
        `pip install barterdude[prometheus]`
    """)


def partial_metric(cls: MetricWrapperBase, registry: CollectorRegistry):

    class RegistryMetric(cls):
        __init__ = functools.partialmethod(cls.__init__, registry=registry)

    return RegistryMetric

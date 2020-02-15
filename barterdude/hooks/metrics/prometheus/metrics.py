from prometheus_client.metrics import MetricWrapperBase
from prometheus_client import (
    Counter,
    Gauge,
    Summary,
    Histogram,
    Info,
    Enum
)
class Metric:
    def __init__(self,
                 name,
                 documentation,
                 labelnames,
                 namespace,
                 subsystem,
                 unit,
                 labelvalues,
                 registry,
                 kwargs):
        self.__name = name
        self.__documentation = documentation
        self.__labelnames = labelnames
        self.__namespace = namespace
        self.__subsystem = subsystem
        self.__unit = unit
        self.__labelvalues = labelvalues
        self.__registry = registry
        self.__kwargs = kwargs

    @property
    def counter(self):
        return Counter(
            name=self.__name,
            documentation=self.__documentation,
            labelnames=self.__labelnames,
            namespace=self.__namespace,
            subsystem=self.__subsystem,
            unit=self.__unit,
            labelvalues=self.__labelvalues,
            registry=self.__registry,
            **kwargs
        )

    @property
    def gauge(self):
        return Gauge(
            name=self.__name,
            documentation=self.__documentation,
            labelnames=self.__labelnames,
            namespace=self.__namespace,
            subsystem=self.__subsystem,
            unit=self.__unit,
            labelvalues=self.__labelvalues,
            registry=self.__registry,
            **self.__kwargs
        )

    @property
    def summary(self):
        return Summary(
            name=self.__name,
            documentation=self.__documentation,
            labelnames=self.__labelnames,
            namespace=self.__namespace,
            subsystem=self.__subsystem,
            unit=self.__unit,
            labelvalues=self.__labelvalues,
            registry=self.__registry,
            **self.__kwargs
        )

    @property
    def histogram(self):
        return Histogram(
            name=self.__name,
            documentation=self.__documentation,
            labelnames=self.__labelnames,
            namespace=self.__namespace,
            subsystem=self.__subsystem,
            unit=self.__unit,
            labelvalues=self.__labelvalues,
            registry=self.__registry,
            **self.__kwargs
        )

    @property
    def info(self, **kwargs):
        return Info(
            name=self.__name,
            documentation=self.__documentation,
            labelnames=self.__labelnames,
            namespace=self.__namespace,
            subsystem=self.__subsystem,
            unit=self.__unit,
            labelvalues=self.__labelvalues,
            registry=self.__registry,
            **self.__kwargs
        )

    @property
    def enum(self, **kwargs):
        return Enum(
            name=self.__name,
            documentation=self.__documentation,
            labelnames=self.__labelnames,
            namespace=self.__namespace,
            subsystem=self.__subsystem,
            unit=self.__unit,
            labelvalues=self.__labelvalues,
            registry=self.__registry,
            **self.__kwargs
        )
    

class Metrics(dict):

    def __setitem__(self, name: str, metric: MetricWrapperBase):
        if name in self:
            value = self.__getitem__(name)
            raise ValueError(
                f"Key {name} already exists with value {value}"
            )
        super(Metrics, self).__setitem__(name, metric)

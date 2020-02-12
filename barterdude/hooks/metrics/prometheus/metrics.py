try:
    from prometheus_client.metrics import MetricWrapperBase
except ImportError:
    raise ImportError("""
    Please install extra dependency with:
        `pip install barterdude[prometheus]`
    """)


class Metrics(dict):

    def __setitem__(self, name: str, metric: MetricWrapperBase):
        if name in self:
            value = self.__getitem__(name)
            raise ValueError(
                f"Key {name} already exists with value {value}"
            )
        super(Metrics, self).__setitem__(name, metric)

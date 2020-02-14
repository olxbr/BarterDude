from prometheus_client.metrics import MetricWrapperBase


class Metrics(dict):

    def __setitem__(self, name: str, metric: MetricWrapperBase):
        if name in self:
            value = self.__getitem__(name)
            raise ValueError(
                f"Key {name} already exists with value {value}"
            )
        super(Metrics, self).__setitem__(name, metric)

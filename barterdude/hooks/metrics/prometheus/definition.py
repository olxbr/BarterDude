try:
    from prometheus_client import (
        Counter,
        Histogram
    )
except ImportError:
    print("""
    Please install extra dependency with:
        `pip install barterdude[prometheus]`
    """)
from barterdude.hooks.metrics.prometheus.metrics import Metrics


class Definition:

    TIME_UNIT = "seconds"

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

    def prepare_before_consume(self, name, default_kwargs: dict):
        self.metrics[name] = Counter(
                name="received_number_before_consume",
                documentation="Messages that worker received from queue(s)",
                **default_kwargs
            )

    def prepare_on_complete(self, state, default_kwargs: dict):
        default_kwargs["labelnames"] += ["state", "error"]

        self.metrics[state] = Counter(
                name=f"consumed_number_on_{state}",
                documentation=(f"Messages that worker consumed with {state}"
                               " from queue(s)"),
                **default_kwargs
            )

    def prepare_time_measure(self, name, default_kwargs: dict):
        default_kwargs["labelnames"] += ["state", "error"]
        default_kwargs["unit"] = self.TIME_UNIT

        self.metrics[name] = Histogram(
                name="time_spent_processing_message",
                documentation=("Time spent when function was "
                               "processing a message"),
                buckets=self.__histogram_buckets,
                **default_kwargs
            )

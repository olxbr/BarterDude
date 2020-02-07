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
from barterdude.hooks.metrics.prometheus.senders import Senders


class Definition:

    TIME_UNIT = "seconds"

    def __init__(
        self,
        histogram_buckets: tuple = Histogram.DEFAULT_BUCKETS,
        senders: Senders = Senders()
    ):
        self.__histogram_buckets = histogram_buckets
        self.__senders = senders

    @property
    def senders(self):
        return self.__senders

    def prepare_before_consume(self, name, default_kwargs: dict):
        self.senders[name] = Counter(
                name="received_number_before_consume",
                documentation="Messages that worker received from queue(s)",
                **default_kwargs
            )

    def prepare_on_complete(self, state, default_kwargs: dict):
        default_kwargs["labelnames"] += ["state", "error"]

        self.senders[state] = Counter(
                name=f"consumed_number_on_{state}",
                documentation=(f"Messages that worker consumed with {state}"
                               " from queue(s)"),
                **default_kwargs
            )

    def prepare_time_measure(self, name, default_kwargs: dict):
        default_kwargs["labelnames"] += ["state", "error"]
        default_kwargs["unit"] = self.TIME_UNIT

        self.senders[name] = Histogram(
                name="time_spent_processing_message",
                documentation=("Time spent when function was "
                               "processing a message"),
                buckets=self.__histogram_buckets,
                **default_kwargs
            )

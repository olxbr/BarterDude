try:
    from prometheus_client.metrics import MetricWrapperBase
except ImportError:
    print("""
    Please install extra dependency with:
        `pip install barterdude[prometheus]`
    """)


class Senders(dict):

    def __setitem__(self, name: str, sender: MetricWrapperBase):
        if name in self.keys():
            value = self.__getitem__(name)
            raise ValueError(
                f"Key {name} already exists with value {value}"
            )
        super(Senders, self).__setitem__(name, sender)

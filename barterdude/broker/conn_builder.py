from kombu import Connection


class ConnBuilder:
    def __init__(self, settings: dict):
        self.__settings = settings

    def __call__(self):
        return Connection(**self.__settings())

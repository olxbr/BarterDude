from barterdude.hooks import BaseHook


class Prometheus(BaseHook):
    def __init__(self, gateway_url: str):
        self.__gateway_url = gateway_url

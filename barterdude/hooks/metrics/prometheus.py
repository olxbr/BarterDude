from barterdude import BarterDude
from barterdude.hooks import HttpHook


class Prometheus(HttpHook):
    def __init__(self, barterdude: BarterDude, path: str = "/metrics"):
        super(Prometheus, self).__init__(barterdude, path)

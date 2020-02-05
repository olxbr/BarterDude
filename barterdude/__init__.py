from asyncworker import App
from typing import Iterable


class BarterDude(App):
    def forward(
        self,
        conn_name: str,
        exchanges: Iterable[str],
        vhost: str = "",
        routing_key: str = ""

    ):
        def wrapper(f, message):
            for exchange in exchanges:
                self.get_connection(conn_name).put(
                    body=message,
                    routing_key=routing_key,
                    exchange=exchange,
                    vhost=vhost
                )

            return f

        return wrapper

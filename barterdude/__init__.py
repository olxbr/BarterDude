from asyncworker import App
from typing import Iterable
from barterdude.monitor import Monitor


class BarterDude(App):
    def forward(
        self,
        conn_name: str,
        exchanges: Iterable[str],
        vhost: str = "",
        routing_key: str = ""

    ):
        def decorator(f):
            def wrapper(message):
                returned = f(message)
                for exchange in exchanges:
                    self.get_connection(conn_name).put(
                        body=message,
                        routing_key=routing_key,
                        exchange=exchange,
                        vhost=vhost
                    )
                return returned

            return wrapper

        return decorator

    def observe(self, monitor: Monitor):
        def decorator(f):
            def wrapper(message):
                monitor.dispatch_before_consume(message)
                try:
                    returned = f(message)
                except Exception as error:
                    monitor.dispatch_on_fail(message, error)
                    raise error
                monitor.dispatch_on_success(message)
                return returned

            return wrapper

        return decorator

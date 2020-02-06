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
            async def wrapper(message):
                returned = await f(message)
                for exchange in exchanges:
                    await self.get_connection(conn_name).put(
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
            async def wrapper(message):
                await monitor.dispatch_before_consume(message)
                try:
                    returned = await f(message)
                except Exception as error:
                    await monitor.dispatch_on_fail(message, error)
                    raise error
                else:
                    await monitor.dispatch_on_success(message)
                    return returned

            return wrapper

        return decorator

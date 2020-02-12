from asyncio import gather
from asyncworker import App, Options, RouteTypes
from asyncworker.connections import AMQPConnection
from typing import Iterable
from barterdude.monitor import Monitor


class BarterDude():
    def __init__(  # nosec
        self,
        hostname: str = "127.0.0.1",
        username: str = "guest",
        password: str = "guest",
        prefetch: int = 10,
        connection_name: str = "default",
    ):
        self.__connection = AMQPConnection(
            name=connection_name,
            hostname=hostname,
            username=username,
            password=password,
            prefetch=prefetch
        )
        self.__app = App(connections=[self.__connection])

    def add_endpoint(self, routes, methods, hook):
        self.__app.route(
            routes=routes,
            methods=methods,
            type=RouteTypes.HTTP
        )(hook)

    def consume_amqp(
        self,
        queues: Iterable[str],
        monitor: Monitor = Monitor(),
        bulk_size: int = 1,
        bulk_flush_interval: int = 60,
        **kwargs,
    ):
        def decorator(f):
            async def process_message(message):
                body = message.body
                await monitor.dispatch_before_consume(body)
                try:
                    await f(body)
                except Exception as error:
                    await monitor.dispatch_on_fail(body, error)
                    message.reject()
                else:
                    await monitor.dispatch_on_success(body)

            @self.__app.route(
                queues,
                type=RouteTypes.AMQP_RABBITMQ,
                options={
                    Options.BULK_SIZE: bulk_size,
                    Options.BULK_FLUSH_INTERVAL: bulk_flush_interval
                },
                **kwargs
            )
            async def wrapper(messages):
                await gather(*map(process_message, messages))

            return wrapper

        return decorator

    async def publish_amqp(
        self,
        exchange: str,
        data: dict,
        routing_key: str = "",
        **kwargs,
    ):
        await self.__connection.put(
            exchange=exchange,
            data=data,
            routing_key=routing_key,
            **kwargs
        )

    async def startup(self):
        await self.__app.startup()

    async def shutdown(self):
        await self.__app.shutdown()

    def run(self):
        self.__app.run()

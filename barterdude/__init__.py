from asyncio import gather
from asyncworker import App, RouteTypes
from asyncworker.options import Options
from asyncworker.connections import AMQPConnection
from asyncworker.rabbitmq.message import RabbitMQMessage
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
        coroutines: int = 10,
        bulk_flush_interval: float = 60.0,
        max_concurrency: int = 1,
        requeue_on_fail: bool = True
    ):
        def decorator(f):
            async def process_message(message: RabbitMQMessage):
                await monitor.dispatch_before_consume(message)
                try:
                    await f(message)
                except Exception as error:
                    await monitor.dispatch_on_fail(message, error)
                    message.reject(requeue_on_fail)
                else:
                    await monitor.dispatch_on_success(message)

            @self.__app.route(
                queues,
                type=RouteTypes.AMQP_RABBITMQ,
                options={
                    Options.BULK_SIZE: coroutines,
                    Options.BULK_FLUSH_INTERVAL: bulk_flush_interval,
                    Options.MAX_CONCURRENCY: max_concurrency
                }
            )
            async def wrapper(messages: RabbitMQMessage):
                await gather(*map(process_message, messages))

            return wrapper

        return decorator

    async def publish_amqp(
        self,
        exchange: str,
        data: dict,
        properties: dict = None,
        routing_key: str = "",
        **kwargs,
    ):
        await self.__connection.put(
            exchange=exchange,
            data=data,
            properties=properties,
            routing_key=routing_key,
            **kwargs
        )

    async def startup(self):
        await self.__app.startup()

    async def shutdown(self):
        await self.__app.shutdown()

    def run(self):
        self.__app.run()

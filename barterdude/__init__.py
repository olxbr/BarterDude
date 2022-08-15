import json
import traceback
from aiohttp import web
from asyncio import gather
from asyncworker import App, RouteTypes
from asyncworker.options import Options
from asyncworker.connections import AMQPConnection
from asyncworker.rabbitmq.message import RabbitMQMessage
from collections import MutableMapping
from typing import Iterable, Optional, Callable, Any, Tuple
from barterdude.monitor import Monitor
from barterdude.message import MessageValidation, ValidationException
from barterdude.mocks import RabbitMQMessageMock, BarterdudeMock


class BarterDude(MutableMapping):
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

    def add_callback_endpoint(
        self,
        routes: Iterable[str],
        hook: Callable,
        mock_dependencies: Iterable[Tuple[Any, str]] = None,
    ):
        def hook_to_callback(req):
            return self._call_callback_endpoint(req, hook, mock_dependencies)

        self.add_endpoint(
            routes=routes,
            methods=['POST'],
            hook=hook_to_callback
        )

    async def _call_callback_endpoint(
        self,
        request: web.Request,
        hook: Callable,
        mock_dependencies: Iterable[Tuple[Any, str]],
    ):
        payload = await request.json()
        body = payload.get('body')
        headers = payload.get('headers')
        should_mock_barterdude = payload.get('should_mock_barterdude', True)

        if body is None:
            return web.Response(
                status=400,
                body=json.dumps({
                    'msg': 'Missing "body" attribute in payload.'
                })
            )

        rabbitmq_message_mock = RabbitMQMessageMock(body, headers)

        barterdude_mock = None
        if should_mock_barterdude:
            barterdude_mock = BarterdudeMock(mock_dependencies)

        response = {}

        try:
            await hook(rabbitmq_message_mock, barterdude=barterdude_mock)
        except Exception:
            response['exception'] = traceback.format_exc()

        response['message_calls'] = rabbitmq_message_mock.get_calls()

        if barterdude_mock is not None:
            response['barterdude_calls'] = barterdude_mock.get_calls()

        return web.Response(status=200, body=json.dumps(response))

    def consume_amqp(
        self,
        queues: Iterable[str],
        monitor: Monitor = Monitor(),
        coroutines: int = 10,
        bulk_flush_interval: float = 60.0,
        requeue_on_fail: bool = True,
        requeue_on_validation_fail: bool = False,
        validation_schema: Optional[dict] = {}
    ):
        msg_validation = MessageValidation(validation_schema)

        def decorator(f):
            async def process_message(message: RabbitMQMessage):
                await monitor.dispatch_before_consume(message)
                try:
                    await f(msg_validation(message))
                except ValidationException as error:
                    await monitor.dispatch_on_fail(message, error)
                    message.reject(requeue_on_validation_fail)
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
                    Options.CONNECTION_FAIL_CALLBACK:
                        monitor.dispatch_on_connection_fail,
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

    def __getitem__(self, key):
        return self.__app[key]

    def __setitem__(self, key, value):
        self.__app[key] = value

    def __delitem__(self, key):
        del self.__app[key]

    def __len__(self):
        return len(self.__app)

    def __iter__(self):
        return iter(self.__app)

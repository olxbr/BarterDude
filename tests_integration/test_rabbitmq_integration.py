import asyncio

from asynctest import TestCase

from barterdude import BarterDude

from asyncworker import RouteTypes
from asyncworker.connections import AMQPConnection


class RabbitMQConsumerTest(TestCase):

    async def setUp(self):
        self.queue_name = "test"
        self.exchange_name = "test_exchange"
        self.output_queue_name = "test_output"
        self.connection_name = "default"
        self.consume_callback_shoud_not_be_called = False
        self.handler_with_requeue_called = 0
        self.handler_without_requeue_called = 0
        self.successful_message_value_is_equal = False
        self.successful_message_value_is_equal_first = False
        self.successful_message_value_is_equal_second = False
        self.connection = AMQPConnection(  # nosec
            name=self.connection_name,
            hostname="127.0.0.1",
            username="guest",
            password="guest",
            prefetch=1
        )
        self.queue_manager = self.connection["/"]
        await self.queue_manager.connection._connect()
        await self.queue_manager.connection.channel.queue_declare(
            self.queue_name
        )
        await self.queue_manager.connection.channel.exchange_declare(
            self.exchange_name, "direct"
        )
        await self.queue_manager.connection.channel.queue_declare(
            self.output_queue_name
        )
        await self.queue_manager.connection.channel.queue_bind(
            self.output_queue_name, self.exchange_name, ""
        )
        self.app = BarterDude(connections=[self.connection])

    async def tearDown(self):
        self.handler_without_requeue_called = 0
        self.handler_with_requeue_called = 0
        await self.queue_manager.connection.channel.queue_delete(
            self.queue_name
        )
        await self.queue_manager.connection.channel.queue_delete(
            self.output_queue_name
        )
        await self.queue_manager.connection.channel.exchange_delete(
            self.exchange_name
        )
        await self.queue_manager.connection.close()

    async def test_process_one_successful_message(self):

        message = {"key": "value"}

        @self.app.route([self.queue_name], type=RouteTypes.AMQP_RABBITMQ)
        async def handler(messages):
            self.successful_message_value_is_equal = (
                messages[0].body["key"] == message["key"]
            )

        await self.app.startup()

        await self.queue_manager.put(routing_key=self.queue_name, data=message)
        await asyncio.sleep(1)
        self.assertTrue(self.successful_message_value_is_equal)
        await self.app.shutdown()

    # async def test_process_one_successful_message_and_forward_exchange(self):

    #     message = {"key": "value"}

    #     @self.app.route([self.queue_name], type=RouteTypes.AMQP_RABBITMQ)
    #     @self.app.forward(self.connection_name, [self.exchange_name])
    #     async def handler(messages):
    #         self.successful_message_value_is_equal_first = (
    #             messages[0].body["key"] == message["key"]
    #         )

    #     @self.app.route([self.output_queue_name],
    #                     type=RouteTypes.AMQP_RABBITMQ)
    #     async def other_handler(messages):
    #         if self.successful_message_value_is_equal_first:
    #             self.successful_message_value_is_equal_second = (
    #                 messages[0].body["key"] == message["key"]
    #             )
    #         else:
    #             self.successful_message_value_is_equal_second = False
    #         self.successful_message_value_is_equal_second = messages

    #     await self.app.startup()

    #     await self.queue_manager.put(
    #       routing_key=self.queue_name, data=message)
    #     await asyncio.sleep(2)
    #     self.assertTrue(self.successful_message_value_is_equal_first)
    #     self.assertTrue(self.successful_message_value_is_equal_second)
    #     await self.app.shutdown()

    async def test_process_message_reject_with_requeue(self):

        @self.app.route([self.queue_name], type=RouteTypes.AMQP_RABBITMQ)
        async def other_handler(messages):
            if self.handler_with_requeue_called > 0:
                messages[0].accept()
            else:
                self.handler_with_requeue_called += 1
            messages[0].field  # AttributeError

        await self.app.startup()

        await self.queue_manager.put(
            routing_key=self.queue_name,
            data={"key": "handler_with_requeue_then_ack"},
        )
        await asyncio.sleep(2)
        self.assertEqual(1, self.handler_with_requeue_called)
        await self.app.shutdown()

    async def test_process_message_reject_without_requeue(self):

        @self.app.route([self.queue_name], type=RouteTypes.AMQP_RABBITMQ)
        async def other_handler(messages):
            self.handler_without_requeue_called += 1
            messages[0].reject(requeue=False)
            messages[0].field  # AttributeError

        await self.app.startup()

        await self.queue_manager.put(
            routing_key=self.queue_name,
            data={"key": "handler_without_requeue"}
        )
        await asyncio.sleep(2)
        self.assertEqual(1, self.handler_without_requeue_called)

        await self.app.shutdown()

        async def callback(*args, **kwargs):
            self.consume_callback_shoud_not_be_called = True

        await self.queue_manager.connection.channel.basic_consume(
            callback, queue_name=self.queue_name
        )
        await asyncio.sleep(5)
        self.assertFalse(
            self.consume_callback_shoud_not_be_called
        )

import asyncio

from asynctest import TestCase, CoroutineMock
from barterdude import BarterDude
from asyncworker.connections import AMQPConnection
from random import choices
from string import ascii_uppercase


class RabbitMQConsumerTest(TestCase):
    use_default_loop = True

    async def setUp(self):
        self.input_queue = "test"
        self.output_exchange = "test_exchange"
        self.output_queue = "test_output"

        self.connection = AMQPConnection(  # nosec
            name="barterdude-test",
            hostname="127.0.0.1",
            username="guest",
            password="guest",
            prefetch=1
        )
        self.queue_manager = self.connection["/"]
        await self.queue_manager.connection._connect()
        await self.queue_manager.connection.channel.queue_declare(
            self.input_queue
        )
        await self.queue_manager.connection.channel.exchange_declare(
            self.output_exchange, "direct"
        )
        await self.queue_manager.connection.channel.queue_declare(
            self.output_queue
        )
        await self.queue_manager.connection.channel.queue_bind(
            self.output_queue, self.output_exchange, ""
        )

        self.messages = []
        for i in range(10):
            message = {"key": "".join(choices(ascii_uppercase, k=16))}
            self.messages.append(message)

        self.app = BarterDude()

    async def tearDown(self):
        await self.queue_manager.connection.channel.queue_delete(
            self.input_queue
        )
        await self.queue_manager.connection.channel.queue_delete(
            self.output_queue
        )
        await self.queue_manager.connection.channel.exchange_delete(
            self.output_exchange
        )
        await self.queue_manager.connection.close()

    async def test_process_ons_successful_message(self):
        handler = CoroutineMock()
        self.app.consume_amqp([self.input_queue])(handler)

        await self.app.startup()
        await self.queue_manager.put(
            routing_key=self.input_queue,
            data=self.messages[0]
        )
        await asyncio.sleep(1)
        handler.assert_called_once_with(self.messages[0])
        await self.app.shutdown()

    async def test_process_one_message_and_publish(self):
        @self.app.consume_amqp([self.input_queue])
        async def forward(message):
            await self.app.publish_amqp(
                self.output_exchange,
                self.messages[1]
            )

        handler = CoroutineMock()
        self.app.consume_amqp([self.output_queue])(handler)

        await self.app.startup()
        await self.queue_manager.put(
            routing_key=self.input_queue,
            data=self.messages[0]
        )
        await asyncio.sleep(1)
        handler.assert_called_once_with(self.messages[1])
        await self.app.shutdown()

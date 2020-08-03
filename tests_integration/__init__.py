import os
import asyncio

from asynctest import TestCase
from barterdude import BarterDude
from barterdude.hook_manager import HookManager
from barterdude.layer.manager import LayerManager
from asyncworker.connections import AMQPConnection
from random import choices
from string import ascii_uppercase


class TestBaseIntegration(TestCase):
    use_default_loop = True

    async def send_all_messages(self):
        futures = []
        for message in self.messages:
            futures.append(self.queue_manager.put(
                routing_key=self.input_queue,
                data=message
            ))
        await asyncio.gather(*futures)

    async def setUp(self):
        self.input_queue = "test"
        self.output_exchange = "test_exchange"
        self.output_queue = "test_output"
        self.rabbitmq_host = os.environ.get("RABBITMQ_HOST", "127.0.0.1")
        self.barterdude_host = os.environ.get("BARTERDUDE_HOST", "127.0.0.1")

        self.connection = AMQPConnection(  # nosec
            name="barterdude-test",
            hostname=self.rabbitmq_host,
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

        self.app = BarterDude(hostname=self.rabbitmq_host)
        layer_manager = LayerManager()
        self.hook_manager = HookManager(layer_manager=layer_manager)

    async def tearDown(self):
        await self.app.shutdown()
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

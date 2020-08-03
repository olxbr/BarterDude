import asyncio

from tests_integration import TestBaseIntegration
from tests_integration.helpers import ErrorHook, StopHook

from barterdude import BarterDude
from barterdude.hooks.logging import Logging


class TestRabbitMQConsumer(TestBaseIntegration):

    async def test_process_messages_successfully(self):
        received_messages = set()

        @self.app.consume_amqp([self.input_queue], coroutines=1)
        async def handler(message):
            nonlocal received_messages
            received_messages.add(message.body["key"])

        await self.app.startup()
        await self.send_all_messages()
        await asyncio.sleep(1)

        for message in self.messages:
            self.assertTrue(message["key"] in received_messages)

    async def test_process_messages_successfully_even_with_crashed_hook(self):
        received_messages = set()

        self.hook_manager.add_for_all_hooks(ErrorHook())

        @self.app.consume_amqp(
            [self.input_queue], coroutines=1, hook_manager=self.hook_manager)
        async def handler(message):
            nonlocal received_messages
            received_messages.add(message.body["key"])

        await self.app.startup()
        await self.send_all_messages()
        await asyncio.sleep(1)

        for message in self.messages:
            self.assertIn(message["key"], received_messages)

    async def test_not_process_messages_successfully_with_stop_hook(self):
        received_messages = set()

        self.hook_manager.add_for_all_hooks(StopHook())

        @self.app.consume_amqp(
            [self.input_queue], coroutines=1, hook_manager=self.hook_manager)
        async def handler(message):
            nonlocal received_messages
            received_messages.add(message.body["key"])

        await self.app.startup()
        await self.send_all_messages()
        await asyncio.sleep(1)

        for message in self.messages:
            self.assertNotIn(message["key"], received_messages)

    async def test_process_one_message_and_publish(self):
        @self.app.consume_amqp([self.input_queue], coroutines=1)
        async def forward(message):
            await self.app.publish_amqp(
                self.output_exchange,
                self.messages[1]
            )

        received_message = None

        @self.app.consume_amqp([self.output_queue], coroutines=1)
        async def handler(message):
            nonlocal received_message
            received_message = message.body

        await self.app.startup()
        await self.queue_manager.put(
            routing_key=self.input_queue,
            data=self.messages[0]
        )
        await asyncio.sleep(1)
        self.assertEqual(received_message, self.messages[1])

    async def test_process_message_reject_without_requeue(self):
        handler_called = 0

        @self.app.consume_amqp(
            [self.input_queue], bulk_flush_interval=1, coroutines=1)
        async def handler(message):
            nonlocal handler_called
            handler_called += 1
            if handler_called < 2:
                raise Exception()

        await self.app.startup()
        await self.queue_manager.put(
            routing_key=self.input_queue,
            data=self.messages[0]
        )
        await asyncio.sleep(2)
        self.assertEqual(handler_called, 1)

    async def test_fails_to_connect_to_rabbitmq(self):

        self.hook_manager.add_for_all_hooks(Logging())

        self.app = BarterDude(hostname="invalid_host")

        @self.app.consume_amqp([self.input_queue], self.hook_manager)
        async def handler(message):
            pass

        await self.app.startup()
        with self.assertLogs("barterdude") as cm:
            await asyncio.sleep(2)

        self.assertIn(
            "{'message': 'Failed to connect to the broker', 'retries': 1,",
            cm.output[0]
        )

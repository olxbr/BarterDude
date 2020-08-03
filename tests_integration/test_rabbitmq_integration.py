import os
import asyncio

from asynctest import TestCase
from barterdude import BarterDude
from barterdude.layer.manager import LayerManager
from barterdude.hook_manager import HookManager
from barterdude.hooks.logging import Logging
from barterdude.hooks.requeue import Requeue
from barterdude.hooks.retry import Retry
from barterdude.hooks.schema_validation import SchemaValidation
from barterdude.exceptions import StopFailFlowException
from tests_unit.helpers import load_fixture
from tests_integration.helpers import ErrorHook, StopHook
from asyncworker.connections import AMQPConnection
from random import choices
from string import ascii_uppercase


class RabbitMQConsumerTest(TestCase):
    use_default_loop = True

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

        self.schema = load_fixture("schema.json")

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

    async def send_all_messages(self):
        futures = []
        for message in self.messages:
            futures.append(self.queue_manager.put(
                routing_key=self.input_queue,
                data=message
            ))
        await asyncio.gather(*futures)

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

    async def test_process_messages_successfully_with_validation(self):
        received_messages = set()

        self.hook_manager.add_for_all_hooks(
            SchemaValidation(self.schema))

        @self.app.consume_amqp(
            [self.input_queue], coroutines=1, hook_manager=self.hook_manager)
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

    async def test_process_message_reject_with_requeue(self):
        handler_called = 0

        @self.app.consume_amqp(
            [self.input_queue], requeue_on_fail=True,
            bulk_flush_interval=1, coroutines=1)
        async def handler(messages):
            nonlocal handler_called
            handler_called += 1
            if handler_called < 2:
                raise Exception()

        await self.app.startup()
        await self.queue_manager.put(
            routing_key=self.input_queue,
            data=self.messages[0]
        )
        await asyncio.sleep(1)
        self.assertEqual(handler_called, 2)

    async def test_process_message_reject_without_requeue(self):
        handler_called = 0

        @self.app.consume_amqp(
            [self.input_queue], requeue_on_fail=False,
            bulk_flush_interval=1, coroutines=1)
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

    async def test_process_message_reject_with_requeue_hook(self):
        handler_called = 0

        self.hook_manager.add_for_all_hooks(
            Requeue(requeue_on_fail=True))

        @self.app.consume_amqp(
            [self.input_queue], requeue_on_fail=False,
            bulk_flush_interval=1, coroutines=1,
            hook_manager=self.hook_manager)
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
        self.assertEqual(handler_called, 2)

    async def test_process_message_no_requeue_by_validation_with_requeue(self):
        handler_called = 0

        self.hook_manager.add_for_all_hooks(
            SchemaValidation(requeue_on_fail=False))

        @self.app.consume_amqp(
            [self.input_queue], hook_manager=self.hook_manager,
            bulk_flush_interval=1, coroutines=1, requeue_on_fail=True)
        async def handler(messages):
            nonlocal handler_called
            handler_called += 1
            if handler_called < 2:
                raise StopFailFlowException()

        await self.app.startup()
        await self.queue_manager.put(
            routing_key=self.input_queue,
            data=self.messages[0]
        )
        await asyncio.sleep(2)
        self.assertEqual(handler_called, 1)

    async def test_process_message_reject_by_validation_without_requeue(self):
        handler_called = 0

        self.hook_manager.add_for_all_hooks(
            SchemaValidation(requeue_on_fail=False))

        @self.app.consume_amqp(
            [self.input_queue], hook_manager=self.hook_manager,
            bulk_flush_interval=1, coroutines=1)
        async def handler(messages):
            nonlocal handler_called
            handler_called += 1
            if handler_called < 2:
                raise StopFailFlowException()

        await self.app.startup()
        await self.queue_manager.put(
            routing_key=self.input_queue,
            data=self.messages[0]
        )
        await asyncio.sleep(2)
        self.assertEqual(handler_called, 1)

    async def test_process_message_reject_by_validation_with_requeue(self):
        handler_called = 0

        self.hook_manager.add_for_all_hooks(
            SchemaValidation(requeue_on_fail=True)
        )

        @self.app.consume_amqp(
            [self.input_queue], hook_manager=self.hook_manager,
            bulk_flush_interval=1, coroutines=1)
        async def handler(messages):
            nonlocal handler_called
            handler_called += 1
            if handler_called < 2:
                raise StopFailFlowException()

        await self.app.startup()
        await self.queue_manager.put(
            routing_key=self.input_queue,
            data=self.messages[0]
        )
        await asyncio.sleep(2)
        self.assertEqual(handler_called, 2)

    async def test_process_message_reject_by_validation_before_handler(self):
        handler_called = 0

        self.hook_manager.add_for_all_hooks(
            SchemaValidation(self.schema)
        )

        @self.app.consume_amqp(
            [self.input_queue], hook_manager=self.hook_manager)
        async def handler(messages):
            nonlocal handler_called
            handler_called += 1

        await self.app.startup()
        await self.queue_manager.put(
            routing_key=self.input_queue,
            data={"wrong": "key"}
        )
        await asyncio.sleep(1)
        self.assertEqual(handler_called, 0)

    async def test_process_messages_and_requeue_only_one(self):
        first_read = set()
        second_read = set()

        @self.app.consume_amqp(
            [self.input_queue],
            coroutines=len(self.messages),
            bulk_flush_interval=0.1
        )
        async def handler(message):
            nonlocal first_read
            nonlocal second_read
            value = message.body["key"]
            if value not in first_read:
                first_read.add(value)
                if message.body == self.messages[0]:
                    # process only messages[0] again
                    raise Exception()
            else:
                second_read.add(value)

        await self.app.startup()
        await self.send_all_messages()

        await asyncio.sleep(1)

        for message in self.messages:
            self.assertTrue(message["key"] in first_read)

        self.assertSetEqual(second_read, {self.messages[0]["key"]})

    async def test_process_message_with_retry(self):
        handler_called = 0

        self.hook_manager.add_for_all_hooks(
            Retry(max_tries=3, backoff_base_ms=2))

        @self.app.consume_amqp(
            [self.input_queue], requeue_on_fail=False,
            bulk_flush_interval=1, coroutines=1,
            hook_manager=self.hook_manager)
        async def handler(message):
            nonlocal handler_called
            handler_called += 1
            raise Exception()

        await self.app.startup()
        await self.queue_manager.put(
            routing_key=self.input_queue,
            data=self.messages[0]
        )
        await asyncio.sleep(4)
        self.assertEqual(handler_called, 3)

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

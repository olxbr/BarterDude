import asyncio

from tests_integration import TestBaseIntegration
from tests_unit.helpers import load_fixture

from barterdude.hooks.schema_validation import SchemaValidation
from barterdude.exceptions import StopFailFlowException


class TestSchemaValidationIntegration(TestBaseIntegration):

    async def setUp(self):
        await super().setUp()
        self.schema = load_fixture("schema.json")

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

    async def test_process_message_reject_by_validation_without_requeue(self):
        handler_called = 0

        self.hook_manager.add_for_all_hooks(
            SchemaValidation(self.schema, requeue_on_fail=False))

        @self.app.consume_amqp(
            [self.input_queue], hook_manager=self.hook_manager,
            bulk_flush_interval=1, coroutines=1)
        async def handler(messages):
            nonlocal handler_called
            handler_called += 1

        await self.app.startup()
        await self.queue_manager.put(
            routing_key=self.input_queue,
            data={"wrong": "key"}
        )
        await asyncio.sleep(2)
        self.assertEqual(handler_called, 0)

    async def test_process_message_validation_without_requeue(self):
        handler_called = 0

        self.hook_manager.add_for_all_hooks(
            SchemaValidation(requeue_on_fail=False)
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
        self.assertEqual(handler_called, 1)

    async def test_process_message_validation_with_requeue(self):
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

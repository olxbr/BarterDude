import asyncio

from tests_integration import TestBaseIntegration
from tests_unit.helpers import load_fixture

from barterdude.hooks.schema_validation import SchemaValidation
from barterdude.hooks.requeue import Requeue
from barterdude.exceptions import StopFailFlowException


class TestMixHooksIntegration(TestBaseIntegration):

    async def setUp(self):
        await super().setUp()
        self.schema = load_fixture("schema.json")

    async def test_process_message_no_requeue_by_validation_with_requeue(self):
        handler_called = 0

        self.hook_manager.add_for_all_hooks(
            Requeue(requeue_on_fail=True)
        )
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

    async def test_process_message_reject_by_validation_without_requeue(self):
        handler_called = 0

        self.hook_manager.add_for_all_hooks(
            Requeue(requeue_on_fail=True)
        )
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

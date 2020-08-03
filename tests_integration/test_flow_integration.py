import asyncio

from tests_integration import TestBaseIntegration
from tests_integration.helpers import ErrorHook, StopHook, RestartHook


class TestFlowIntegration(TestBaseIntegration):

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

    async def test_process_messages_successfully_3_times_restart_hook(self):
        received_messages = list()

        self.hook_manager.add_for_all_hooks(RestartHook())

        @self.app.consume_amqp(
            [self.input_queue], coroutines=1, hook_manager=self.hook_manager)
        async def handler(message):
            nonlocal received_messages
            received_messages.append(message.body)

        await self.app.startup()
        await self.queue_manager.put(
            routing_key=self.input_queue,
            data=self.messages[0]
        )
        await asyncio.sleep(1)

        self.assertEqual(3, len(received_messages))
        for message in received_messages:
            self.assertDictEqual(self.messages[0], message)

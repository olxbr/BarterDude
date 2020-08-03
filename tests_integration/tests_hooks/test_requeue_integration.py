import asyncio

from tests_integration import TestBaseIntegration
from barterdude.hooks.requeue import Requeue


class TestRequeueIntegration(TestBaseIntegration):

    async def test_process_message_reject_with_requeue_hook(self):
        handler_called = 0

        self.hook_manager.add_for_all_hooks(
            Requeue(requeue_on_fail=True))

        @self.app.consume_amqp(
            [self.input_queue], bulk_flush_interval=1, coroutines=1,
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

    async def test_process_messages_and_requeue_only_one(self):
        first_read = set()
        second_read = set()

        self.hook_manager.add_for_all_hooks(
            Requeue(requeue_on_fail=True))

        @self.app.consume_amqp(
            [self.input_queue], coroutines=len(self.messages),
            bulk_flush_interval=0.1, hook_manager=self.hook_manager
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

    async def test_process_message_reject_without_requeue(self):
        handler_called = 0

        self.hook_manager.add_for_all_hooks(
            Requeue(requeue_on_fail=False))

        @self.app.consume_amqp(
            [self.input_queue], bulk_flush_interval=1, coroutines=1,
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
        self.assertEqual(handler_called, 1)

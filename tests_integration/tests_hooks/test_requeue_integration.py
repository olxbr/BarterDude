import asyncio

from tests_integration import TestBaseIntegration
from barterdude.hooks.requeue import Requeue


class TestRequeueIntegration(TestBaseIntegration):

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

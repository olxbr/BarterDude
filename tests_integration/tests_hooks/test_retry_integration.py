import asyncio

from tests_integration import TestBaseIntegration
from barterdude.hooks.retry import Retry


class TestRetryIntegration(TestBaseIntegration):

    async def test_process_message_with_retry(self):
        handler_called = 0

        self.hook_manager.add_for_all_hooks(
            Retry(max_tries=3, backoff_base_ms=2))

        @self.app.consume_amqp(
            [self.input_queue], bulk_flush_interval=1, coroutines=1,
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
        await asyncio.sleep(2)
        self.assertEqual(handler_called, 3)

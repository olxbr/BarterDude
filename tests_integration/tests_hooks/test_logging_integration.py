import asyncio

from tests_integration import TestBaseIntegration
from barterdude.hooks import logging as hook_logging


class TestLoggingIntegration(TestBaseIntegration):

    async def test_print_logs_redacted(self):
        hook_logging.BARTERDUDE_LOG_REDACTED = True
        self.hook_manager.add_for_all_hooks(hook_logging.Logging())
        error = Exception("raise expected")

        @self.app.consume_amqp([self.input_queue], self.hook_manager)
        async def handler(message):
            if message.body == self.messages[0]:
                raise error

        with self.assertLogs("barterdude") as cm:
            await self.app.startup()
            await self.queue_manager.put(
                routing_key=self.input_queue,
                data=self.messages[0]
            )
            await asyncio.sleep(2)

        key = self.messages[0]["key"]
        error_str = repr(error)

        self.assertIn("'message': 'Before consume message'", cm.output[0])
        self.assertNotIn(
            f"'message_body': '{{\"key\": \"{key}\"}}'", cm.output[0]
        )
        self.assertIn("'delivery_tag': 1", cm.output[0])

        self.assertIn("'message': 'Failed to consume message'", cm.output[1])
        self.assertNotIn(
            f"'message_body': '{{\"key\": \"{key}\"}}'", cm.output[1]
        )
        self.assertIn("'delivery_tag': 1", cm.output[1])
        self.assertIn(f"'exception': \"{error_str}\"", cm.output[1])
        self.assertIn("'traceback': [", cm.output[1])

    async def test_print_logs(self):
        hook_logging.BARTERDUDE_LOG_REDACTED = False
        self.hook_manager.add_for_all_hooks(hook_logging.Logging())
        error = Exception("raise expected")

        @self.app.consume_amqp([self.input_queue], self.hook_manager)
        async def handler(message):
            if message.body == self.messages[0]:
                raise error

        with self.assertLogs("barterdude") as cm:
            await self.app.startup()
            await self.queue_manager.put(
                routing_key=self.input_queue,
                data=self.messages[0]
            )
            await asyncio.sleep(2)

        key = self.messages[0]["key"]
        error_str = repr(error)

        self.assertIn("'message': 'Before consume message'", cm.output[0])
        self.assertIn(
            f"'message_body': '{{\"key\": \"{key}\"}}'", cm.output[0]
        )
        self.assertIn("'delivery_tag': 1", cm.output[0])

        self.assertIn("'message': 'Failed to consume message'", cm.output[1])
        self.assertIn(
            f"'message_body': '{{\"key\": \"{key}\"}}'", cm.output[1]
        )
        self.assertIn("'delivery_tag': 1", cm.output[1])
        self.assertIn(f"'exception': \"{error_str}\"", cm.output[1])
        self.assertIn("'traceback': [", cm.output[1])

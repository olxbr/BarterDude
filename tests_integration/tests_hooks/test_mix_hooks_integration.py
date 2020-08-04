import aiohttp
import asyncio

from tests_integration import TestBaseIntegration
from tests_unit.helpers import load_fixture

from barterdude.hooks.schema_validation import SchemaValidation
from barterdude.hooks.requeue import Requeue
from barterdude.exceptions import StopFailFlowException
from barterdude.hooks.healthcheck import Healthcheck
from barterdude.hooks.retry import Retry


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

    async def test_healthcheck_doesnt_count_retry(self):
        handler_called = 0

        schema_validation = SchemaValidation(requeue_on_fail=False)
        healthcheck = Healthcheck(self.app)
        retry = Retry(max_tries=3, backoff_base_ms=2)

        self.hook_manager.add_before_consume(
            schema_validation,
            healthcheck
        )
        self.hook_manager.add_on_connection_fail(healthcheck)
        self.hook_manager.add_on_success(healthcheck)
        self.hook_manager.add_on_fail(retry)
        self.hook_manager.add_on_fail(
            schema_validation,
            healthcheck
        )

        @self.app.consume_amqp(
            [self.input_queue], hook_manager=self.hook_manager,
            bulk_flush_interval=1, coroutines=1)
        async def handler(messages):
            nonlocal handler_called
            handler_called += 1
            raise Exception()

        await self.app.startup()
        await self.queue_manager.put(
            routing_key=self.input_queue,
            data=self.messages[0]
        )
        await asyncio.sleep(2)
        async with aiohttp.ClientSession() as session:
            timeout = aiohttp.ClientTimeout(total=1)
            url = f'http://{self.barterdude_host}:8080/healthcheck'
            async with session.get(url, timeout=timeout) as response:
                status_code = response.status
                text = await response.text()

        self.assertEqual(handler_called, 3)
        self.assertEqual(status_code, 500)
        self.assertEqual(
            text,
            '{"message": "Success rate: 0.0 (expected: 0.95)", '
            '"fail": 1, "success": 0, "status": "fail"}'
        )

    async def test_schema_validation_not_counting_healthcheck(self):
        handler_called = 0

        schema_validation = SchemaValidation(
            self.schema, requeue_on_fail=False)
        healthcheck = Healthcheck(self.app)
        retry = Retry(max_tries=3, backoff_base_ms=2)

        self.hook_manager.add_before_consume(
            schema_validation,
            healthcheck
        )
        self.hook_manager.add_on_connection_fail(healthcheck)
        self.hook_manager.add_on_success(healthcheck)
        self.hook_manager.add_on_fail(retry)
        self.hook_manager.add_on_fail(
            schema_validation,
            healthcheck
        )

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
        async with aiohttp.ClientSession() as session:
            timeout = aiohttp.ClientTimeout(total=1)
            url = f'http://{self.barterdude_host}:8080/healthcheck'
            async with session.get(url, timeout=timeout) as response:
                status_code = response.status
                text = await response.text()

        self.assertEqual(handler_called, 0)
        self.assertEqual(status_code, 200)
        self.assertEqual(
            text,
            '{"message": "No messages in last 60.0s", "status": "ok"}'
        )

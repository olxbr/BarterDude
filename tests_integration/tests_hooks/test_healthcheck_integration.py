import aiohttp
import asyncio

from tests_integration import TestBaseIntegration
from tests_integration.helpers import ErrorHook
from barterdude.hooks.healthcheck import Healthcheck


class TestHealthcheckIntegration(TestBaseIntegration):

    async def test_obtains_healthcheck(self):

        self.hook_manager.add_for_all_hooks(Healthcheck(self.app))

        @self.app.consume_amqp([self.input_queue], self.hook_manager)
        async def handler(message):
            pass

        await self.app.startup()
        await self.queue_manager.put(
            routing_key=self.input_queue,
            data=self.messages[0]
        )
        await asyncio.sleep(1)

        async with aiohttp.ClientSession() as session:
            timeout = aiohttp.ClientTimeout(total=1)
            url = f'http://{self.barterdude_host}:8080/healthcheck'
            async with session.get(url, timeout=timeout) as response:
                status_code = response.status
                text = await response.text()

        self.assertEqual(status_code, 200)
        self.assertEqual(
            text,
            '{"message": "Success rate: 1.0 (expected: 0.95)", '
            '"fail": 0, "success": 1, "status": "ok"}'
        )

    async def test_obtains_healthcheck_even_with_crashed_hook(self):

        self.hook_manager.add_for_all_hooks(
            ErrorHook(),
            Healthcheck(self.app)
        )

        @self.app.consume_amqp([self.input_queue], self.hook_manager)
        async def handler(message):
            pass

        await self.app.startup()
        await self.queue_manager.put(
            routing_key=self.input_queue,
            data=self.messages[0]
        )
        await asyncio.sleep(1)

        async with aiohttp.ClientSession() as session:
            timeout = aiohttp.ClientTimeout(total=1)
            url = f'http://{self.barterdude_host}:8080/healthcheck'
            async with session.get(url, timeout=timeout) as response:
                status_code = response.status
                text = await response.text()

        self.assertEqual(status_code, 200)
        self.assertEqual(
            text,
            '{"message": "Success rate: 1.0 (expected: 0.95)", '
            '"fail": 0, "success": 1, "status": "ok"}'
        )

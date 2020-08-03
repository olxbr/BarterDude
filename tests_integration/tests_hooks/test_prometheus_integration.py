import aiohttp
import asyncio

from tests_integration import TestBaseIntegration
from barterdude.hooks.metrics.prometheus import Prometheus


class TestPrometheusIntegration(TestBaseIntegration):

    async def test_obtains_prometheus_metrics(self):
        labels = {"app_name": "barterdude_consumer"}
        self.hook_manager.add_for_all_hooks(Prometheus(self.app, labels))

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
            url = f'http://{self.barterdude_host}:8080/metrics'
            async with session.get(url, timeout=timeout) as response:
                status_code = response.status
                text = await response.text()

        self.assertEqual(status_code, 200)
        self.assertNotEqual(-1, text.find(
            'barterdude_received_number_before_consume_messages_total'
            '{app_name="barterdude_consumer"} 1.0'))
        self.assertNotEqual(-1, text.find(
            'barterdude_processing_message_seconds_bucket{app_name='
            '"barterdude_consumer",error="",le="0.025",state="success"} 1.0'
        ))
        self.assertNotEqual(-1, text.find(
            'barterdude_processing_message_seconds_count'
            '{app_name="barterdude_consumer",error="",state="success"} 1.0'
        ))

    async def test_obtains_prometheus_metrics_without_labels(self):
        self.hook_manager.add_for_all_hooks(Prometheus(self.app))

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
            url = f'http://{self.barterdude_host}:8080/metrics'
            async with session.get(url, timeout=timeout) as response:
                status_code = response.status
                text = await response.text()

        self.assertEqual(status_code, 200)
        self.assertNotEqual(-1, text.find(
            'barterdude_received_number_before_consume_messages_total 1.0'
        ))
        self.assertNotEqual(-1, text.find(
            'barterdude_processing_message_seconds_bucket'
            '{error="",le="0.025",state="success"} 1.0'
        ))
        self.assertNotEqual(-1, text.find(
            'barterdude_processing_message_seconds_count'
            '{error="",state="success"} 1.0'
        ))

    async def test_register_multiple_prometheus_hooks(self):
        """This test raised the following error:
           ValueError: Duplicated timeseries in CollectorRegistry"""

        self.hook_manager.add_for_all_hooks(
            Prometheus(self.app, {"app_name": "barterdude1"}, "/metrics1"),
            Prometheus(self.app, {"app_name": "barterdude2"}, "/metrics2"),
        )

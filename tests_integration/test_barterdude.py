import os
import aiohttp
import asyncio

from asynctest import TestCase
from barterdude import BarterDude
from barterdude.monitor import Monitor
from barterdude.hooks.healthcheck import Healthcheck
from barterdude.hooks import logging as hook_logging
from barterdude.hooks.metrics.prometheus import Prometheus
from tests_unit.helpers import load_fixture
from tests_integration.helpers import ErrorHook
from asyncworker.connections import AMQPConnection
from random import choices
from string import ascii_uppercase


class TestBarterDude(TestCase):
    use_default_loop = True

    async def setUp(self):
        self.input_queue = "test"
        self.output_exchange = "test_exchange"
        self.output_queue = "test_output"
        self.rabbitmq_host = os.environ.get("RABBITMQ_HOST", "127.0.0.1")
        self.barterdude_host = os.environ.get("BARTERDUDE_HOST", "127.0.0.1")

        self.connection = AMQPConnection(  # nosec
            name="barterdude-test",
            hostname=self.rabbitmq_host,
            username="guest",
            password="guest",
            prefetch=1
        )
        self.queue_manager = self.connection["/"]
        await self.queue_manager.connection._connect()
        await self.queue_manager.connection.channel.queue_declare(
            self.input_queue
        )
        await self.queue_manager.connection.channel.exchange_declare(
            self.output_exchange, "direct"
        )
        await self.queue_manager.connection.channel.queue_declare(
            self.output_queue
        )
        await self.queue_manager.connection.channel.queue_bind(
            self.output_queue, self.output_exchange, ""
        )

        self.messages = []
        for i in range(10):
            message = {"key": "".join(choices(ascii_uppercase, k=16))}
            self.messages.append(message)

        self.schema = load_fixture("schema.json")

        self.app = BarterDude(hostname=self.rabbitmq_host)

    async def tearDown(self):
        await self.app.shutdown()
        await self.queue_manager.connection.channel.queue_delete(
            self.input_queue
        )
        await self.queue_manager.connection.channel.queue_delete(
            self.output_queue
        )
        await self.queue_manager.connection.channel.exchange_delete(
            self.output_exchange
        )
        await self.queue_manager.connection.close()

    async def test_obtains_healthcheck(self):
        monitor = Monitor(Healthcheck(self.app))

        @self.app.consume_amqp([self.input_queue], monitor)
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
        monitor = Monitor(ErrorHook(), Healthcheck(self.app))

        @self.app.consume_amqp([self.input_queue], monitor)
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

    async def test_obtains_prometheus_metrics(self):
        labels = {"app_name": "barterdude_consumer"}
        monitor = Monitor(Prometheus(self.app, labels))

        @self.app.consume_amqp([self.input_queue], monitor)
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
        monitor = Monitor(Prometheus(self.app))

        @self.app.consume_amqp([self.input_queue], monitor)
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

        Monitor(
            Prometheus(self.app, {"app_name": "barterdude1"}, "/metrics1"),
            Prometheus(self.app, {"app_name": "barterdude2"}, "/metrics2"),
        )

    async def test_print_logs_redacted(self):
        hook_logging.BARTERDUDE_LOG_REDACTED = True
        monitor = Monitor(hook_logging.Logging())
        error = Exception("raise expected")

        @self.app.consume_amqp([self.input_queue], monitor)
        async def handler(message):
            if message.body == self.messages[0]:
                raise error

        with self.assertLogs("barterdude") as cm:
            await self.app.startup()
            await self.queue_manager.put(
                routing_key=self.input_queue,
                data=self.messages[0]
            )
            await asyncio.sleep(1)

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
        monitor = Monitor(hook_logging.Logging())
        error = Exception("raise expected")

        @self.app.consume_amqp([self.input_queue], monitor)
        async def handler(message):
            if message.body == self.messages[0]:
                raise error

        with self.assertLogs("barterdude") as cm:
            await self.app.startup()
            await self.queue_manager.put(
                routing_key=self.input_queue,
                data=self.messages[0]
            )
            await asyncio.sleep(1)

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

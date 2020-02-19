import aiohttp
import asyncio

from asynctest import TestCase
from barterdude import BarterDude
from barterdude.monitor import Monitor
from barterdude.hooks.healthcheck import Healthcheck
from barterdude.hooks.logging import Logging
from barterdude.hooks.metrics.prometheus import Prometheus
from asyncworker.connections import AMQPConnection
from random import choices
from string import ascii_uppercase


class RabbitMQConsumerTest(TestCase):
    use_default_loop = True

    async def setUp(self):
        self.input_queue = "test"
        self.output_exchange = "test_exchange"
        self.output_queue = "test_output"

        self.connection = AMQPConnection(  # nosec
            name="barterdude-test",
            hostname="127.0.0.1",
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

        self.app = BarterDude()

    async def tearDown(self):
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

    async def send_all_messages(self):
        futures = []
        for message in self.messages:
            futures.append(self.queue_manager.put(
                routing_key=self.input_queue,
                data=message
            ))
        await asyncio.gather(*futures)

    async def test_process_messages_successfully(self):
        received_messages = set()

        @self.app.consume_amqp([self.input_queue], coroutines=1)
        async def handler(message):
            nonlocal received_messages
            received_messages.add(message.body["key"])

        await self.app.startup()
        await self.send_all_messages()
        await asyncio.sleep(1)

        for message in self.messages:
            self.assertTrue(message["key"] in received_messages)

        await self.app.shutdown()

    async def test_process_one_message_and_publish(self):
        @self.app.consume_amqp([self.input_queue], coroutines=1)
        async def forward(message):
            await self.app.publish_amqp(
                self.output_exchange,
                self.messages[1]
            )

        received_message = None

        @self.app.consume_amqp([self.output_queue], coroutines=1)
        async def handler(message):
            nonlocal received_message
            received_message = message.body

        await self.app.startup()
        await self.queue_manager.put(
            routing_key=self.input_queue,
            data=self.messages[0]
        )
        await asyncio.sleep(1)
        self.assertEquals(received_message, self.messages[1])
        await self.app.shutdown()

    async def test_process_message_requeue_with_requeue(self):
        handler_called = 0

        @self.app.consume_amqp([self.input_queue], coroutines=1)
        async def handler(messages):
            nonlocal handler_called
            handler_called = handler_called + 1
            if handler_called < 2:
                raise Exception()

        await self.app.startup()
        await self.queue_manager.put(
            routing_key=self.input_queue,
            data=self.messages[0]
        )
        await asyncio.sleep(1)
        self.assertEquals(handler_called, 2)
        await self.app.shutdown()

    async def test_process_message_reject_with_requeue(self):
        handler_called = 0

        @self.app.consume_amqp([self.input_queue], requeue_on_fail=False)
        async def handler(messages):
            nonlocal handler_called
            handler_called = handler_called + 1
            if handler_called < 2:
                raise Exception()

        await self.app.startup()
        await self.queue_manager.put(
            routing_key=self.input_queue,
            data=self.messages[0]
        )
        await asyncio.sleep(1)
        self.assertEquals(handler_called, 1)
        await self.app.shutdown()

    async def test_process_message_reject_without_requeue(self):
        handler_called = 0

        @self.app.consume_amqp([self.input_queue])
        async def handler(message):
            nonlocal handler_called
            handler_called = handler_called + 1
            message.reject(requeue=False)

        await self.app.startup()
        await self.queue_manager.put(
            routing_key=self.input_queue,
            data=self.messages[0]
        )
        await asyncio.sleep(1)
        self.assertEquals(handler_called, 1)
        await self.app.shutdown()

    async def test_process_messages_and_requeue_only_one(self):
        first_read = set()
        second_read = set()

        @self.app.consume_amqp(
            [self.input_queue],
            coroutines=len(self.messages),
            bulk_flush_interval=0.1
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

        await self.app.shutdown()

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
            url = 'http://localhost:8080/healthcheck'
            async with session.get(url, timeout=timeout) as response:
                status_code = response.status
                text = await response.text()

        self.assertEquals(status_code, 200)
        self.assertEquals(text, "Bater like a pro! Success rate: 1.0")

        await self.app.shutdown()

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
            url = 'http://localhost:8080/metrics'
            async with session.get(url, timeout=timeout) as response:
                status_code = response.status
                text = await response.text()

        self.assertEquals(status_code, 200)
        self.assertNotEquals(-1, text.find(
            'barterdude_received_number_before_consume_messages_total'
            '{app_name="barterdude_consumer"} 1.0'))

        await self.app.shutdown()

    async def test_print_logs(self):
        monitor = Monitor(Logging())
        error = Exception("raise expected")

        @self.app.consume_amqp([self.input_queue], monitor)
        async def handler(message):
            if message.body == self.messages[0]:
                raise error

        await self.app.startup()

        with self.assertLogs("barterdude") as cm:
            await self.queue_manager.put(
                routing_key=self.input_queue,
                data=self.messages[0]
            )
            await asyncio.sleep(1)

        message_str = repr(self.messages[0])
        error_str = repr(error)
        self.assertEqual(
            cm.output[0],
            f"INFO:barterdude:going to consume message: {message_str}"
        )
        self.assertTrue(
            f"ERROR:barterdude:failed to consume message: {message_str}\n"
            f"{error_str}\n" in cm.output[1]
        )

        await self.app.shutdown()

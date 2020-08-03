from asynctest import TestCase, Mock
from datetime import datetime
from barterdude.hooks.retry import Retry
from barterdude.message import Message
from barterdude.exceptions import RestartFlowException


class TestRetry(TestCase):
    def setUp(self):
        self.rbmq_message = Mock(Message)
        self.rbmq_message.properties.headers = dict()

    async def test_should_run_without_max_fail(self):
        retry = Retry(2)
        with self.assertRaises(RestartFlowException):
            await retry.on_fail(self.rbmq_message, Exception())
        self.assertEqual(
            self.rbmq_message.properties.headers["x-fail-tries"],
            1
        )

    async def test_should_run_with_max_fail(self):
        retry = Retry(1)
        await retry.on_fail(self.rbmq_message, Exception())
        self.rbmq_message.reject.assert_called_once_with(False)
        self.assertEqual(
            self.rbmq_message.properties.headers["x-fail-tries"],
            1
        )

    async def test_should_run_with_max_fail_twice(self):
        retry = Retry(2)
        with self.assertRaises(RestartFlowException):
            await retry.on_fail(self.rbmq_message, Exception())
        await retry.on_fail(self.rbmq_message, Exception())
        self.rbmq_message.reject.assert_called_once_with(False)
        self.assertEqual(
            self.rbmq_message.properties.headers["x-fail-tries"],
            2
        )

    async def test_should_apply_backoff_multiple_times(self):
        retry = Retry(4, 10)
        before_time = datetime.now()
        with self.assertRaises(RestartFlowException):
            await retry.on_fail(self.rbmq_message, Exception())
        after_time = datetime.now()
        datediff = after_time - before_time
        self.assertGreaterEqual(datediff.total_seconds(), 0.01)
        self.assertLessEqual(datediff.total_seconds(), 0.02)

        before_time = datetime.now()
        with self.assertRaises(RestartFlowException):
            await retry.on_fail(self.rbmq_message, Exception())
        after_time = datetime.now()
        datediff = after_time - before_time
        self.assertGreaterEqual(datediff.total_seconds(), 0.1)
        self.assertLessEqual(datediff.total_seconds(), 0.2)

        before_time = datetime.now()
        with self.assertRaises(RestartFlowException):
            await retry.on_fail(self.rbmq_message, Exception())
        after_time = datetime.now()
        datediff = after_time - before_time
        self.assertAlmostEqual(datediff.seconds, 1)

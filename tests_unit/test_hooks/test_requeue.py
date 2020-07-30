from asynctest import TestCase, Mock
from barterdude.hooks.requeue import Requeue
from barterdude.message import Message


class TestRequeue(TestCase):
    def setUp(self):
        self.rbmq_message = Mock(Message)

    async def test_should_run_message_with_requeue(self):
        requeue = Requeue(requeue_on_fail=True)
        await requeue.on_fail(self.rbmq_message, Exception())
        self.rbmq_message.reject.assert_called_once_with(True)

    async def test_should_run_message_without_requeue(self):
        requeue = Requeue(requeue_on_fail=False)
        await requeue.on_fail(self.rbmq_message, Exception())
        self.rbmq_message.reject.assert_called_once_with(False)

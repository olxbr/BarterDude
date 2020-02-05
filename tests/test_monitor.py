from asynctest import TestCase, Mock, CoroutineMock
from barterdude.monitor import Monitor


class TestMonitor(TestCase):

    def setUp(self):
        self.hook1 = Mock()
        self.hook2 = Mock()
        self.monitor = Monitor(self.hook1, self.hook2)

    async def test_should_call_hooks_before_consume(self):
        self.hook1.before_consume = CoroutineMock()
        self.hook2.before_consume = CoroutineMock()
        await self.monitor.dispatch_before_consume({})
        self.hook1.before_consume.assert_called_once()
        self.hook2.before_consume.assert_called_once()
        self.hook1.before_consume.assert_called_with({})
        self.hook2.before_consume.assert_called_with({})

    async def test_should_call_hooks_on_success(self):
        self.hook1.on_success = CoroutineMock()
        self.hook2.on_success = CoroutineMock()
        await self.monitor.dispatch_on_success({})
        self.hook1.on_success.assert_called_once()
        self.hook2.on_success.assert_called_once()
        self.hook1.on_success.assert_called_with({})
        self.hook2.on_success.assert_called_with({})

    async def test_should_call_hooks_on_fail(self):
        exception = Exception()
        self.hook1.on_fail = CoroutineMock()
        self.hook2.on_fail = CoroutineMock()
        await self.monitor.dispatch_on_fail({}, exception)
        self.hook1.on_fail.assert_called_once()
        self.hook2.on_fail.assert_called_once()
        self.hook1.on_fail.assert_called_with({}, exception)
        self.hook2.on_fail.assert_called_with({}, exception)

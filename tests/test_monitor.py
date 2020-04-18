from asynctest import TestCase, MagicMock, Mock, CoroutineMock, patch
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

    async def test_should_call_hooks_on_connection_fail(self):
        exception = Mock()
        retries = Mock()
        self.hook1.on_connection_fail = CoroutineMock()
        self.hook2.on_connection_fail = CoroutineMock()
        await self.monitor.dispatch_on_connection_fail(exception, retries)
        self.hook1.on_connection_fail.assert_called_once()
        self.hook2.on_connection_fail.assert_called_once()
        self.hook1.on_connection_fail.assert_called_with(exception, retries)
        self.hook2.on_connection_fail.assert_called_with(exception, retries)

    @patch("barterdude.monitor.repr")
    @patch("barterdude.monitor.format_tb")
    async def test_should_log_if_hook_fail(self, format_tb, repr):
        logger = MagicMock()
        exception = Exception()

        async def before_consume(msg):
            raise exception
        self.monitor._logger = logger
        self.hook1.before_consume = before_consume
        self.hook2.before_consume = CoroutineMock()
        await self.monitor.dispatch_before_consume({})
        repr.assert_called_once_with(exception)
        format_tb.assert_called_once_with(exception.__traceback__)
        logger.error.assert_called_once_with({
            "message": f"Error on hook method {before_consume}",
            "exception": repr.return_value,
            "traceback": format_tb.return_value,
        })
        self.hook2.before_consume.assert_called_with({})

from asynctest import TestCase, MagicMock, Mock, CoroutineMock, patch
from barterdude.hook_manager import HookManager
from barterdude.exceptions import StopFailFlowException


class TestHookManager(TestCase):

    def setUp(self):
        self.layer_manager = Mock()
        self.hook_manager = HookManager(self.layer_manager)

    async def test_should_call_hooks_before_consume(self):
        self.hook1.before_consume = CoroutineMock()
        self.hook2.before_consume = CoroutineMock()
        await self.hook_manager.dispatch_before_consume({})
        self.hook1.before_consume.assert_called_once()
        self.hook2.before_consume.assert_called_once()
        self.hook1.before_consume.assert_called_with({})
        self.hook2.before_consume.assert_called_with({})

    async def test_should_call_hooks_on_success(self):
        self.hook1.on_success = CoroutineMock()
        self.hook2.on_success = CoroutineMock()
        await self.hook_manager.dispatch_on_success({})
        self.hook1.on_success.assert_called_once()
        self.hook2.on_success.assert_called_once()
        self.hook1.on_success.assert_called_with({})
        self.hook2.on_success.assert_called_with({})

    async def test_should_call_hooks_on_fail(self):
        exception = Exception()
        self.hook1.on_fail = CoroutineMock()
        self.hook2.on_fail = CoroutineMock()
        await self.hook_manager.dispatch_on_fail({}, exception)
        self.hook1.on_fail.assert_called_once()
        self.hook2.on_fail.assert_called_once()
        self.hook1.on_fail.assert_called_with({}, exception)
        self.hook2.on_fail.assert_called_with({}, exception)

    async def test_should_call_hooks_on_connection_fail(self):
        exception = Mock()
        retries = Mock()
        self.hook1.on_connection_fail = CoroutineMock()
        self.hook2.on_connection_fail = CoroutineMock()
        await self.hook_manager.dispatch_on_connection_fail(exception, retries)
        self.hook1.on_connection_fail.assert_called_once()
        self.hook2.on_connection_fail.assert_called_once()
        self.hook1.on_connection_fail.assert_called_with(exception, retries)
        self.hook2.on_connection_fail.assert_called_with(exception, retries)

    @patch("barterdude.hook_manager.repr")
    @patch("barterdude.hook_manager.format_tb")
    async def test_should_log_if_hook_fail(self, format_tb, repr):
        logger = MagicMock()
        exception = Exception()

        async def before_consume(msg):
            raise exception
        self.hook_manager._logger = logger
        self.hook1.before_consume = before_consume
        self.hook2.before_consume = CoroutineMock()
        await self.hook_manager.dispatch_before_consume({})
        repr.assert_called_once_with(exception)
        format_tb.assert_called_once_with(exception.__traceback__)
        logger.error.assert_called_once_with({
            "message": f"Error on hook method {before_consume}",
            "exception": repr.return_value,
            "traceback": format_tb.return_value,
        })
        self.hook2.before_consume.assert_called_with({})

    @patch("barterdude.hook_manager.format_tb")
    async def test_should_not_log_or_continue_if_hook_fail_with_stop(
            self, format_tb):
        logger = MagicMock()
        exception = StopFailFlowException()

        async def before_consume(msg):
            raise exception
        self.hook_manager._logger = logger
        self.hook1.before_consume = before_consume
        self.hook2.before_consume = CoroutineMock()
        with self.assertRaises(StopFailFlowException):
            await self.hook_manager.dispatch_before_consume({})
        format_tb.assert_not_called()
        logger.error.assert_not_called()
        self.hook2.before_consume.assert_called_with({})

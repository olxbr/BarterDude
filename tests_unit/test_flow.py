from asynctest import TestCase, CoroutineMock, Mock
from barterdude.flow import Flow
from barterdude.exceptions import (
    StopFailFlowException, StopSuccessFlowException, RestartFlowException
)


class TestFlow(TestCase):
    def setUp(self):
        self.callback = CoroutineMock()
        self.flow = Flow(self.callback)

    async def test_should_call_callback_on_process(self):
        message = Mock()
        await self.flow.process(message)
        self.callback.assert_awaited_once_with(message)

    async def test_should_pass_with_stop_exceptions(self):
        message = Mock()
        self.callback.side_effect = StopSuccessFlowException()
        await self.flow.process(message)
        self.callback.assert_awaited_once_with(message)
        self.callback.reset_mock()
        self.callback.side_effect = StopFailFlowException()
        await self.flow.process(message)
        self.callback.assert_awaited_once_with(message)

    async def test_should_rerun_with_restart_exception(self):
        message = Mock()
        count = 0

        async def callback(message):
            nonlocal count
            message()
            if count == 0:
                count += 1
                raise RestartFlowException()

        flow = Flow(callback)
        await flow.process(message)
        self.assertEqual(message.call_count, 2)

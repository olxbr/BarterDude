from barterdude.hooks import BaseHook
from barterdude.exceptions import StopFailFlowException, RestartFlowException
from barterdude.message import Message


class ErrorHook(BaseHook):
    async def on_success(self, message: Message):
        raise NotImplementedError()

    async def on_fail(self, message: Message, error: Exception):
        raise NotImplementedError()

    async def before_consume(self, message: Message):
        raise NotImplementedError()

    async def on_connection_fail(self, error: Exception, retries: int):
        raise NotImplementedError()


class StopHook(BaseHook):
    async def before_consume(self, message: Message):
        raise StopFailFlowException()


class RestartHook(BaseHook):

    async def on_success(self, message: Message):
        if not message.properties.headers:
            message.properties.headers = 0
        message.properties.headers += 1
        if message.properties.headers < 3:
            raise RestartFlowException()

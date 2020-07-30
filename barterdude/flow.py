from barterdude.message import Message
from barterdude.exceptions import (
    RestartFlowException, StopFailFlowException, StopSuccessFlowException
)


class Flow:
    def __init__(self, callback):
        self._callback = callback

    async def process(self, message: Message):
        try:
            await self._callback(message)
        except (StopFailFlowException, StopSuccessFlowException):
            pass
        except RestartFlowException:
            await self.process(message)

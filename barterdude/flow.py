from barterdude.message import Message
from barterdude.conf import getLogger
from barterdude.exceptions import (
    RestartFlowException, StopFailFlowException, StopSuccessFlowException
)


class Flow:
    def __init__(self, callback):
        self._callback = callback
        self._logger = getLogger("flow")

    async def process(self, message: Message):
        try:
            await self._callback(message)
        except (StopFailFlowException, StopSuccessFlowException) as e:
            self._logger.debug(repr(e))
        except RestartFlowException as e:
            self._logger.info(repr(e))
            await self.process(message)

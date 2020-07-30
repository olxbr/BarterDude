from barterdude.hooks import BaseHook
from barterdude.message import Message


class Requeue(BaseHook):
    def __init__(
            self,
            requeue_on_fail: bool = True):
        self._requeue_on_fail = requeue_on_fail

    async def on_fail(self, message: Message, error: Exception):
        message.reject(self._requeue_on_fail)

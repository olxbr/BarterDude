import asyncio
from barterdude.hooks import BaseHook
from barterdude.exceptions import RestartFlowException
from barterdude.message import Message


class Retry(BaseHook):
    def __init__(
            self,
            max_tries: int,
            backoff_base_ms: int = 0):
        self._max_tries = max_tries
        self._backoff = backoff_base_ms

    async def on_fail(self, message: Message, error: Exception):
        if not message.properties.headers:
            message.properties.headers = {}
        fail_tries = message.properties.headers.get("fail_tries", 0)
        fail_tries += 1
        message.properties.headers["fail_tries"] = fail_tries
        if self._max_tries == fail_tries:
            return message.reject(False)
        await asyncio.sleep(self._backoff ** fail_tries / 1000)
        raise RestartFlowException()

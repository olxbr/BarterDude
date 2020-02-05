from abc import ABC


class BaseHook(ABC):
    async def on_success(self, message):
        return NotImplemented

    async def on_fail(self, message):
        return NotImplemented

    async def before_consume(self, message):
        return NotImplemented

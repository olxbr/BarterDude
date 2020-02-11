from asyncio import gather


class Monitor:
    def __init__(self, *hooks):
        self.__hooks = hooks

    async def dispatch_before_consume(self, message):
        await gather(*[hook.before_consume(message) for hook in self.__hooks])

    async def dispatch_on_success(self, message):
        await gather(*[hook.on_success(message) for hook in self.__hooks])

    async def dispatch_on_fail(self, message, error):
        await gather(*[hook.on_fail(message, error) for hook in self.__hooks])

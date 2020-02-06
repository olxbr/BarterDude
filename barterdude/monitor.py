class Monitor:
    def __init__(self, *hooks):
        self.__hooks = hooks

    async def dispatch_before_consume(self, message):
        for hook in self.__hooks:
            await hook.before_consume(message)

    async def dispatch_on_success(self, message):
        for hook in self.__hooks:
            await hook.on_success(message)

    async def dispatch_on_fail(self, message, error):
        for hook in self.__hooks:
            await hook.on_fail(message, error)

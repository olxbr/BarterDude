from barterdude.hooks import BaseHook


class Monitor:
    __hooks = []

    def add_hook(self, hook: BaseHook):
        self.__hooks.append(hook)

    async def dispatch_before_consume(self, message):
        for hook in self.__hooks:
            hook.before_consume(message)

    async def dispatch_on_success(self, message):
        for hook in self.__hooks:
            hook.on_success(message)

    async def dispatch_on_fail(self, message, error):
        for hook in self.__hooks:
            hook.on_fail(message)

from barterdude.hooks import BaseHook


class Layer:
    def __init__(self, identifier):
        self._identifier = identifier
        self._hooks = []

    @property
    def identifier(self):
        return self._identifier

    @property
    def hooks(self):
        return tuple(self._hooks)

    def add(self, hook: BaseHook):
        self._hooks.append(hook)

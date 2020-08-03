from barterdude.hooks import BaseHook
from typing import Iterable, Optional, Any
from barterdude.conf import getLogger
from barterdude.message import Message
from barterdude.layer.manager import LayerManager
from barterdude.hook_manager.runner import Runner
from barterdude.layer.default_manager import DefaultLayerManager
from barterdude.layer import Layer


class HookManager(Runner):

    BEFORE_CONSUME = "before_consume"
    ON_SUCCESS = "on_success"
    ON_FAIL = "on_fail"
    ON_CONNECTION_FAIL = "on_connection_fail"

    def __init__(self, layer_manager: LayerManager = DefaultLayerManager()):
        self._layers = layer_manager
        self._logger = getLogger("hook_manager")

    def _add_hooks_by_callback(self, layer: Layer, *hooks: Iterable[BaseHook]):
        for hook in hooks:
            if isinstance(hook, BaseHook):
                layer.add(hook)
        self._layers.store(layer)

    async def _dispatch_by_identifier(self, identifier: str,
                                      subject: Any,
                                      error: Optional[Exception] = None):

        for layer in self._layers.get(identifier):
            if error:
                callbacks = self._prepare_callbacks(
                    identifier, subject, layer.hooks, error)
            else:
                callbacks = self._prepare_callbacks(
                    identifier, subject, layer.hooks)
            await self._run(callbacks)

    def add_before_consume(self, *hooks: Iterable[BaseHook]):
        layer = self._layers.new(self.BEFORE_CONSUME)
        self._add_hooks_by_callback(layer, *hooks)

    def add_on_success(self, *hooks: Iterable[BaseHook]):
        layer = self._layers.new(self.ON_SUCCESS)
        self._add_hooks_by_callback(layer, *hooks)

    def add_on_fail(self, *hooks: Iterable[BaseHook]):
        layer = self._layers.new(self.ON_FAIL)
        self._add_hooks_by_callback(layer, *hooks)

    def add_on_connection_fail(self, *hooks: Iterable[BaseHook]):
        layer = self._layers.new(self.ON_CONNECTION_FAIL)
        self._add_hooks_by_callback(layer, *hooks)

    def add_for_all_hooks(self, *hooks: Iterable[BaseHook]):
        self.add_before_consume(*hooks)
        self.add_on_success(*hooks)
        self.add_on_fail(*hooks)
        self.add_on_connection_fail(*hooks)

    def log_layers(self):
        self._logger.info(str(self._layers))

    async def dispatch_before_consume(self, message: Message):
        identifier = self.BEFORE_CONSUME
        await self._dispatch_by_identifier(identifier, message)

    async def dispatch_on_success(self, message: Message):
        identifier = self.ON_SUCCESS
        await self._dispatch_by_identifier(identifier, message)

    async def dispatch_on_fail(self, message: Message,
                               error: Exception):
        identifier = self.ON_FAIL
        await self._dispatch_by_identifier(identifier, message, error)

    async def dispatch_on_connection_fail(
            self, retries: int, error: Exception
    ):
        identifier = self.ON_CONNECTION_FAIL
        await self._dispatch_by_identifier(identifier, retries, error)

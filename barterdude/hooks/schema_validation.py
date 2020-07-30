import jsonschema
from functools import partial
from typing import Optional
from barterdude.hooks import BaseHook
from barterdude.exceptions import StopFailFlowException
from barterdude.message import Message


class SchemaValidation(BaseHook):
    def __init__(
            self,
            validation_schema: Optional[dict] = {},
            requeue_on_fail: bool = False):
        self._validate = bool(validation_schema)
        self._requeue_on_fail = requeue_on_fail
        resolver = jsonschema.RefResolver.from_schema(validation_schema)
        self._builder = partial(
            jsonschema.validate,
            schema=validation_schema,
            resolver=resolver
        )

    async def on_fail(self, message: Message, error: Exception):
        message.reject(self._requeue_on_fail)

    async def before_consume(self, message: Message):
        if self._validate:
            try:
                self._builder(message.body)
            except jsonschema.ValidationError as err:
                raise StopFailFlowException(err)

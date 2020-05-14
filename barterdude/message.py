import jsonschema
from functools import partial
from typing import Optional, Union
from asyncworker.rabbitmq.message import RabbitMQMessage


class ValidationException(jsonschema.ValidationError):
    pass


class Message:
    def __init__(self, message: RabbitMQMessage):
        self._message = message

    @property
    def body(self):
        return self._message.body

    @property
    def raw(self):
        return self._message.serialized_data

    @property
    def queue_name(self):
        return self._message._amqp_message.queue_name

    @property
    def properties(self):
        return self._message._amqp_message._properties

    def accept(self):
        return self._message.accept()

    def reject(self, requeue=True):
        return self._message.reject(requeue)

    async def process_success(self):
        return await self._message.process_success()

    async def process_exception(self):
        return await self._message.process_exception()


class MessageValidation:
    def __init__(self, validation_schema: Optional[dict] = {}):
        self._validate = bool(validation_schema)
        resolver = jsonschema.RefResolver.from_schema(validation_schema)
        self._builder = partial(
            jsonschema.validate,
            schema=validation_schema,
            resolver=resolver
        )

    def validate(self, message: Union[RabbitMQMessage, Message]):
        if self._validate:
            try:
                self._builder(message.body)
            except jsonschema.ValidationError as err:
                raise ValidationException(err)

    def __call__(self, message: RabbitMQMessage):
        self.validate(message)
        return Message(message)

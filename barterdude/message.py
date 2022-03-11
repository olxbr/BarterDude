import jsonschema
from functools import partial
from typing import Optional, Union
from asyncworker.rabbitmq.message import RabbitMQMessage
from asyncworker.easyqueue.exceptions import UndecodableMessageException


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

    @property
    def envelope(self):
        return self._message._amqp_message._envelope

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
        try:
            body = message.body
            if self._validate:
                self._builder(body)
        except (jsonschema.ValidationError,
                UndecodableMessageException) as err:
            raise ValidationException(err)

    def __call__(self, message: RabbitMQMessage):
        self.validate(message)
        return Message(message)

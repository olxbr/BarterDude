from typing import Optional, Union
from python_jsonschema_objects.validators import ValidationError
from python_jsonschema_objects import ObjectBuilder
from asyncworker.rabbitmq.message import RabbitMQMessage


class ValidationException(ValidationError):
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
        self._builder = ObjectBuilder(validation_schema)

    def validate(self, message: Union[RabbitMQMessage, Message]):
        if self._validate:
            try:
                self._builder.validate(message.body)
            except ValidationError as err:
                raise ValidationException(err)

    def __call__(self, message: RabbitMQMessage):
        self.validate(message)
        return Message(message)

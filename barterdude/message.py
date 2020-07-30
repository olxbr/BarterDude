from asyncworker.rabbitmq.message import RabbitMQMessage


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
    def delivery_tag(self):
        return self._message._delivery_tag

    def accept(self):
        return self._message.accept()

    def reject(self, requeue=True):
        return self._message.reject(requeue)

    async def process_success(self):
        return await self._message.process_success()

    async def process_exception(self):
        return await self._message.process_exception()

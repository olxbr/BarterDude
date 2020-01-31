from kombu import Queue, Message
from seller_bouncer.broker.conn_builder import ConnBuilder
from typing import Callable


class Consumer:
    def __init__(self, connection: ConnBuilder,
                 processer: Callable[[str, Message], bool]
                 ):
        self.__connection = connection
        self.__processer = processer

    async def consume(self, queue: Queue):
        with self.__connection.Consumer(queue) as consumer:
            consumer.register_callback(self.__processer)
            consumer.consume()

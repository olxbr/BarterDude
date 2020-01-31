from kombu import Queue, Connection
from barterdude.message import Message
from typing import Callable, Optional


class Consumer:
    def __init__(self, connection: Connection,
                 processer: Callable[[Message], Optional[dict]]
                 ):
        self.__connection = connection
        self.__processer = processer

    def consume(self, queue: Queue):
        with self.__connection.Consumer(queue) as consumer:
            consumer.register_callback(self.__processer)
            consumer.consume()

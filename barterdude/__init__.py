import logging

from kombu import Exchange, Queue, Connection
from typing import Callable, Optional
from barterdude.message import Message
from barterdude.broker.consumer import Consumer
from barterdude.broker.producer import Producer
from barterdude.callback_handler import CallbackHandler


log = logging.getLogger("barterdude")


def register(callback: Callable[[Message], Optional[dict]],
             queue: Queue, exchange: Exchange, connection: Connection):
    producer = Producer(connection, exchange)
    callback_handler = CallbackHandler(callback, producer)
    consumer = Consumer(connection, callback_handler)
    while True:
        try:
            consumer.consume(queue)
        except Exception as e:
            log.error(e)

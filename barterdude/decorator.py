from typing import Callable, Optional
from kombu import Exchange, Queue, Connection

from barterdude import register
from barterdude.message import Message


def barter(callback: Callable[[Message], Optional[dict]]):
    def wrapper(queue: Queue, exchange: Exchange, connection: Connection):
        register(callback, queue, exchange, connection)

    return wrapper

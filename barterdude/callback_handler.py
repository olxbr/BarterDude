from typing import Callable, Optional
from barterdude.broker.producer import Producer
from barterdude.message import Message


class CallbackHandler:
    def __init__(self,
                 callback: Callable[[Message], Optional[dict]],
                 producer: Producer
                 ):
        self.__callback = callback
        self.__producer = producer

    def __call__(self, *args, **kwargs):
        message = Message(*args, **kwargs)
        result = self.__callback(message)
        if result:
            if type(result) is not dict:
                raise ValueError("Expected dict returning from callback")
            self.__producer.produce(result)
        message.ack()

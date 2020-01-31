from kombu import Message as KombuMessage


class Message(dict):
    def __init__(self, body: str, message: KombuMessage):
        self.__body = body
        self.__message = message

    def as_dict(self):
        return self.__message.payload

    def as_string(self):
        return self.__body

    def ack(self, *args, **kwargs):
        self.__message.ack(*args, **kwargs)

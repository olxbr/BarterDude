from kombu import Exchange
from seller_bouncer.broker.conn_builder import ConnBuilder


class Producer:
    def __init__(self, connection: ConnBuilder):
        self.__connection = connection

    async def produce(self, exchange: Exchange, message: dict):
        self.__connection.Producer().publish(
            message,
            serializer='json',
            exchange=exchange,
            retry=True,
            retry_policy={
                'interval_start': 0,
                'interval_step': 2,
                'interval_max': 6,
                'max_retries': 5,
            }
        )

from kombu import Exchange, Connection


class Producer:
    def __init__(self, connection: Connection, exchange: Exchange):
        self.__connection = connection
        self.__exchange = exchange

    def produce(self, message: dict):
        self.__connection.Producer().publish(
            message,
            serializer='json',
            exchange=self.__exchange,
            retry=True,
            retry_policy={
                'interval_start': 0,
                'interval_step': 2,
                'interval_max': 6,
                'max_retries': 5,
            }
        )

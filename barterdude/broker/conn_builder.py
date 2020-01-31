from kombu import Connection
from seller_bouncer.settings import Settings


class ConnBuilder:
    def __init__(self, settings: Settings = Settings()):
        self.__settings = settings

    def __call__(self):
        return Connection(**self.__get_config_from_settings())

    def __get_config_from_settings(self):
        return dict(
            hostname=self.__settings["rabbitmq_uri"],
            userid=self.__settings["rabbitmq_user"],
            password=self.__settings["rabbitmq_password"]
        )

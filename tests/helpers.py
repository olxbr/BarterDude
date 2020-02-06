from asynctest import Mock, CoroutineMock

from asyncworker.connections import AMQPConnection
from barterdude import BarterDude


class MyApp(BarterDude):
    handlers = (
        Mock(startup=CoroutineMock(), shutdown=CoroutineMock()),
    )


def get_app():
    return MyApp(connections=[AMQPConnection(  # nosec
                name="conn1",
                hostname="localhost",
                username="username",
                password="pass"
            )])

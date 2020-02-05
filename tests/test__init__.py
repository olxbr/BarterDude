from asynctest import Mock, CoroutineMock, TestCase

from barterdude import BarterDude
from asyncworker.connections import AMQPConnection
from asyncworker.easyqueue.queue import JsonQueue


class TestBarterDude(TestCase):
    async def setUp(self):
        class MyApp(BarterDude):
            handlers = (
                Mock(startup=CoroutineMock(), shutdown=CoroutineMock()),
            )
        self.appCls = MyApp
        self.queue = JsonQueue(
            "localhost", "username", "pass"
        )
        self.queue.put = Mock()
        self.queue.consume = Mock()
        self.app = MyApp(connections=[AMQPConnection(  # nosec
                name="conn1",
                hostname="localhost",
                username="username",
                password="pass"
            )])
        self.app.get_connection = Mock(return_value=self.queue)

    async def test_should_call_put(self):
        function = self.app.forward("conn1", ["test"], "vhost", "routing")
        self.queue.put.assert_not_called()
        function(lambda x: None, {})
        self.queue.put.assert_called_once()
        self.queue.put.assert_called_with(
            body={}, exchange='test', routing_key='routing', vhost='vhost'
        )

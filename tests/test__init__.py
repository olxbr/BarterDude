from asynctest import Mock, CoroutineMock, TestCase

from barterdude import BarterDude
from asyncworker.routes import AMQPRoute, RouteTypes
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
        @self.app.forward("conn1", ["test"], "vhost", "routing")
        async def test_decorated(message):
            return None
        self.queue.put.assert_not_called()
        await test_decorated({})
        self.queue.put.assert_called_once()
        self.queue.put.assert_called_with(
            body={}, exchange='test', routing_key='routing', vhost='vhost'
        )

    async def test_should_call_put_when_call_route(self):
        @self.app.route(
            ["test_route"], RouteTypes.AMQP_RABBITMQ
        )
        @self.app.forward(
            "conn1", ["test"], "vhost", "routing"
        )
        async def test_decorated(message):
            return None
        self.queue.put.assert_not_called()
        self.assertEqual(len(self.app.routes_registry), 1)
        self.assertIsInstance(
            self.app.routes_registry[test_decorated], AMQPRoute
        )
        await test_decorated({})
        self.queue.put.assert_called_once()
        self.queue.put.assert_called_with(
            body={}, exchange='test', routing_key='routing', vhost='vhost'
        )

    async def test_should_get_error_when_call_route_inverse_decorated(self):

        @self.app.forward(
            "conn1", ["test"], "vhost", "routing"
        )
        @self.app.route(
            ["test_route"], RouteTypes.AMQP_RABBITMQ
        )
        async def test_decorated(message):
            return None
        self.queue.put.assert_not_called()
        self.assertEqual(len(self.app.routes_registry), 1)

        with self.assertRaises(KeyError):
            self.app.routes_registry[test_decorated]
        await test_decorated({})
        self.queue.put.assert_called_once()
        self.queue.put.assert_called_with(
            body={}, exchange='test', routing_key='routing', vhost='vhost'
        )

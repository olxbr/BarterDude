from asynctest import Mock, TestCase, CoroutineMock
from tests.helpers import get_app

from asyncworker.routes import AMQPRoute, RouteTypes
from asyncworker.easyqueue.queue import JsonQueue

from barterdude.monitor import Monitor


class TestBarterDude(TestCase):
    async def setUp(self):

        self.queue = JsonQueue(
            "localhost", "username", "pass"
        )
        self.queue.put = CoroutineMock()
        self.queue.consume = Mock()
        self.app = get_app()
        self.app.get_connection = Mock(return_value=self.queue)
        self.monitor = Monitor()
        self.monitor.dispatch_before_consume = CoroutineMock()
        self.monitor.dispatch_on_fail = CoroutineMock()
        self.monitor.dispatch_on_success = CoroutineMock()

    async def test_should_call_put_on_forward(self):
        @self.app.forward("conn1", ["test"], "vhost", "routing")
        async def test_decorated(message):
            return None
        self.queue.put.assert_not_called()
        await test_decorated({})
        self.queue.put.assert_called_once()
        self.queue.put.assert_called_with(
            body={}, exchange='test', routing_key='routing', vhost='vhost'
        )

    async def test_should_call_monitor_for_each_success_message(self):

        @self.app.observe(self.monitor)
        async def test_decorated(message):
            return None
        await test_decorated({})
        self.monitor.dispatch_before_consume.assert_called_once()
        self.monitor.dispatch_before_consume.assert_called_with({})
        self.monitor.dispatch_on_success.assert_called_once()
        self.monitor.dispatch_on_success.assert_called_with({})
        self.monitor.dispatch_on_fail.assert_not_called()

    async def test_should_call_monitor_for_each_fail_message(self):

        exception = Exception()
        @self.app.observe(self.monitor)
        async def test_decorated(message):
            raise exception
            return None
        with self.assertRaises(Exception):
            await test_decorated({})
        self.monitor.dispatch_before_consume.assert_called_once()
        self.monitor.dispatch_before_consume.assert_called_with({})
        self.monitor.dispatch_on_fail.assert_called_once()
        self.monitor.dispatch_on_fail.assert_called_with({}, exception)
        self.monitor.dispatch_on_success.assert_not_called()

    async def test_should_call_put_on_forward_when_call_route(self):
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

from asynctest import Mock, TestCase, CoroutineMock, patch, call
from asyncworker import Options, RouteTypes
from barterdude import BarterDude


class TestBarterDude(TestCase):
    @patch("barterdude.App")
    @patch("barterdude.AMQPConnection")
    def setUp(self, AMQPConnection, App):
        self.monitor = Mock()
        self.monitor.dispatch_before_consume = CoroutineMock()
        self.monitor.dispatch_on_success = CoroutineMock()
        self.monitor.dispatch_on_fail = CoroutineMock()
        self.callback = CoroutineMock()
        self.messages = [Mock() for _ in range(10)]
        self.calls = [call(message) for message in self.messages]

        self.AMQPConnection = AMQPConnection
        self.connection = self.AMQPConnection.return_value
        self.App = App
        self.app = self.App.return_value
        self.app.startup = CoroutineMock()
        self.app.shutdown = CoroutineMock()
        self.decorator = self.app.route.return_value

        self.barterdude = BarterDude()

    def test_should_create_connection(self):
        self.AMQPConnection.assert_called_once_with(  # nosec
            hostname="127.0.0.1",
            username="guest",
            password="guest",
            prefetch=10,
            name="default",
        )
        self.App.assert_called_once_with(connections=[self.connection])

    def test_should_call_route_when_created(self):
        self.barterdude.consume_amqp(
            ["queue"]
        )(CoroutineMock())
        self.app.route.assert_called_once_with(
            ["queue"],
            type=RouteTypes.AMQP_RABBITMQ,
            options={
                Options.BULK_SIZE: 10,
                Options.BULK_FLUSH_INTERVAL: 60,
                Options.MAX_CONCURRENCY: 1
            }
        )

    def test_should_call_route_when_adding_endpoint(self):
        hook = Mock()
        self.barterdude.add_endpoint(['/my_route'], ['GET'], hook)
        self.app.route.assert_called_once_with(
            routes=['/my_route'],
            methods=['GET'],
            type=RouteTypes.HTTP
        )
        self.decorator.assert_called_once_with(hook)

    async def test_should_call_callback_for_each_message(self):
        self.barterdude.consume_amqp(["queue"], self.monitor)(self.callback)
        self.decorator.assert_called_once()
        wrapper = self.decorator.call_args[0][0]
        await wrapper(self.messages)
        self.callback.assert_has_calls(self.calls, any_order=True)

    async def test_should_call_reject_when_callback_fail(self):
        self.callback.side_effect = Exception('Boom!')
        self.barterdude.consume_amqp(["queue"], self.monitor)(self.callback)
        wrapper = self.decorator.call_args[0][0]
        await wrapper(self.messages)
        for message in self.messages:
            message.reject.assert_called_once()

    async def test_should_call_monitor_for_each_success_message(self):
        self.barterdude.consume_amqp(["queue"], self.monitor)(self.callback)
        wrapper = self.decorator.call_args[0][0]
        await wrapper(self.messages)
        self.monitor.dispatch_before_consume.assert_has_calls(
            self.calls, any_order=True)
        self.monitor.dispatch_on_success.assert_has_calls(
            self.calls, any_order=True)
        self.monitor.dispatch_on_fail.assert_not_called()

    async def test_should_call_monitor_for_each_fail_message(self):
        error = Exception('Boom!')
        self.callback.side_effect = error
        self.barterdude.consume_amqp(["queue"], self.monitor)(self.callback)
        wrapper = self.decorator.call_args[0][0]
        await wrapper(self.messages)
        self.monitor.dispatch_before_consume.assert_has_calls(
            self.calls, any_order=True)
        error_calls = [call(message, error) for message in self.messages]
        self.monitor.dispatch_on_fail.assert_has_calls(
            error_calls, any_order=True)
        self.monitor.dispatch_on_success.assert_not_called()

    async def test_should_call_put_when_publish(self):
        data = Mock()
        self.connection.put = CoroutineMock()
        await self.barterdude.publish_amqp(
            'exchange',
            data,
            vhost="vhost",
            routing_key="routing_key"
        )
        self.connection.put.assert_called_once_with(
            exchange='exchange',
            data=data,
            vhost="vhost",
            routing_key="routing_key",
            properties=None
        )

    async def test_should_call_startup_and_shutdown(self):
        await self.barterdude.startup()
        self.app.startup.assert_called_once_with()
        await self.barterdude.shutdown()
        self.app.shutdown.assert_called_once_with()

    def test_should_call_run(self):
        self.barterdude.run()
        self.app.run.assert_called_once_with()

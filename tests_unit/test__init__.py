import asyncio
import typing
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock, AsyncMock, patch, call

from asyncworker import Options, RouteTypes
from barterdude import BarterDude
from barterdude.message import Message
from tests_unit.helpers import load_fixture


class TestBarterDude(IsolatedAsyncioTestCase):
    @patch("barterdude.App")
    @patch("barterdude.AMQPConnection")
    def setUp(self, AMQPConnection, App):
        self.monitor = Mock()
        self.monitor.dispatch_before_consume = AsyncMock()
        self.monitor.dispatch_on_success = AsyncMock()
        self.monitor.dispatch_on_fail = AsyncMock()
        self.callback = AsyncMock()
        self.messages = [Mock(value=i) for i in range(10)]
        self.calls = [call(message) for message in self.messages]

        self.AMQPConnection = AMQPConnection
        self.connection = self.AMQPConnection.return_value
        self.App = App
        self.app = self.App.return_value
        self.app.startup = AsyncMock()
        self.app.shutdown = AsyncMock()
        self.decorator = self.app.route.return_value
        self.schema = load_fixture("schema.json")
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
        monitor = Mock()
        self.barterdude.consume_amqp(
            ["queue"], monitor=monitor
        )(AsyncMock())
        self.app.route.assert_called_once_with(
            ["queue"],
            type=RouteTypes.AMQP_RABBITMQ,
            options={
                Options.BULK_SIZE: 10,
                Options.BULK_FLUSH_INTERVAL: 60,
                Options.CONNECTION_FAIL_CALLBACK:
                    monitor.dispatch_on_connection_fail,
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

    async def test_should_call_route_when_adding_callback_endpoint(self):
        hook = Mock()
        self.barterdude.add_callback_endpoint(
            ['/my_route'],
            hook,
            [(Mock(), 'service')]
        )
        self.app.route.assert_called_once_with(
            routes=['/my_route'],
            methods=['POST'],
            type=RouteTypes.HTTP
        )
        self.decorator.assert_called_once()

    async def test_hook_to_callback_should_be_async_and_typed(self):
        bd = BarterDude()
        bd.add_endpoint = Mock()

        hook = Mock()
        bd.add_callback_endpoint(
            ['/my_route'],
            hook,
            [(Mock(), 'service')]
        )

        internal_hook = bd.add_endpoint.call_args_list[0][1].get('hook')
        assert asyncio.iscoroutinefunction(internal_hook) is True
        assert 'req' in typing.get_type_hints(internal_hook)

    async def test_should_hook_call_on_callback_endpoint(self):
        async def mock_hook(message, barterdude):
            barterdude['service'].method_one()
            await barterdude['service'].method_two()
            message.accept()
            await barterdude.publish_amqp(data={'a': 1})

        request = Mock()
        request.json = AsyncMock(return_value={'body': {}})
        service_mock = Mock()
        service_mock.method_one.return_value = 123
        service_mock.method_two = AsyncMock(return_value=234)
        dependencies = [(service_mock, 'service')]
        response = await self.barterdude._call_callback_endpoint(
            request, mock_hook, dependencies)

        request.json.assert_called_once()
        service_mock.method_one.assert_called_once()
        service_mock.method_two.assert_called_once()
        assert response.status == 200
        assert response.body._value == (
            b'{"message_calls": [{"method": "accept", "args": [],'
            b' "kwargs": {}}], "barterdude_calls": [{"method": '
            b'"publish_amqp", "args": [], "kwargs": {"data": {"a": 1}}}]}'
        )

    async def test_should_hook_call_on_callback_endpoint_without_body(self):
        async def mock_hook(message, barterdude):
            barterdude['service'].method_one()
            await barterdude['service'].method_two()
            message.accept()
            await barterdude.publish_amqp(data={'a': 1})

        request = Mock()
        request.json = AsyncMock(return_value={})
        service_mock = Mock()
        service_mock.method_one.return_value = 123
        service_mock.method_two = AsyncMock(return_value=234)
        dependencies = [(service_mock, 'service')]
        response = await self.barterdude._call_callback_endpoint(
            request, mock_hook, dependencies)

        request.json.assert_called_once()
        service_mock.method_one.assert_not_called()
        service_mock.method_two.assert_not_called()
        assert response.status == 400
        expected_msg = b'{"msg": "Missing \\"body\\" attribute in payload."}'
        assert response.body._value == expected_msg

    async def test_should_hook_call_on_callback_endpoint_with_exception(self):
        async def mock_hook(message, barterdude):
            raise Exception

        request = Mock()
        request.json = AsyncMock(return_value={'body': {}})
        service_mock = Mock()
        dependencies = [(service_mock, 'service')]
        response = await self.barterdude._call_callback_endpoint(
            request, mock_hook, dependencies)

        request.json.assert_called_once()
        assert response.status == 200
        assert b'exception' in response.body._value
        assert b'message_calls' in response.body._value
        assert b'barterdude_calls' in response.body._value

    async def test_should_hook_call_on_callback_endpoint_with_dependency(self):
        async def mock_hook(message, barterdude):
            barterdude['service'].method_one()
            barterdude['service'].method_two()
            message.accept()
            await barterdude.publish_amqp(data={'a': 1})

        request = Mock()
        request.json = AsyncMock()
        service_mock = Mock()
        service_mock.method_one.return_value = 123
        service_mock.method_two = AsyncMock(return_value=234)
        dependencies = [(service_mock, 'service')]
        response = await self.barterdude._call_callback_endpoint(
            request, mock_hook, dependencies)

        request.json.assert_called_once()
        service_mock.method_one.assert_called_once()
        service_mock.method_two.assert_called_once()
        assert response.status == 200
        assert response.body._value == (
            b'{"message_calls": [{"method": "accept", "args": [],'
            b' "kwargs": {}}], "barterdude_calls": [{"method": '
            b'"publish_amqp", "args": [], "kwargs": {"data": {"a": 1}}}]}'
        )

    async def test_should_call_callback_for_each_message(self):
        self.barterdude.consume_amqp(["queue"], self.monitor)(self.callback)
        self.decorator.assert_called_once()
        wrapper = self.decorator.call_args[0][0]
        await wrapper(self.messages)
        messages = []
        for message in self.callback.mock_calls:
            self.assertEqual(Message, type(message[1][0]))
            messages.append(message[1][0]._message)
        self.assertListEqual(
            sorted(messages, key=lambda x: x.value),
            sorted(self.messages, key=lambda x: x.value))

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

    async def test_should_call_callback_for_valid_message(self):
        self.barterdude.consume_amqp(
            ["queue"], self.monitor, validation_schema=self.schema
        )(self.callback)
        self.decorator.assert_called_once()
        wrapper = self.decorator.call_args[0][0]
        message = Mock(Message)
        message.body = {"key": 'ok'}
        await wrapper([message])
        self.callback.assert_called_once()
        self.assertEqual(
            self.callback.await_args[0][0].body["key"],
            message.body["key"]
        )

    async def test_should_not_call_callback_for_valid_message(self):
        self.barterdude.consume_amqp(
            ["queue"], self.monitor, validation_schema=self.schema
        )(self.callback)
        self.decorator.assert_called_once()
        wrapper = self.decorator.call_args[0][0]
        message = Mock(Message)
        message.body = {"wrong": 'ok'}
        await wrapper([message])
        self.callback.assert_not_called()

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
        self.connection.put = AsyncMock()
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


class TestAppSharedProperties(IsolatedAsyncioTestCase):
    def setUp(self):
        self.barterdude = BarterDude()

    def test_setitem_changes_state(self):
        self.barterdude["foo"] = foo = Mock()
        self.assertEqual(foo, self.barterdude["foo"])

    async def test_getitem_returns_internal_state_value(self):
        self.barterdude["foo"] = "bar"
        self.assertEqual("bar", self.barterdude["foo"])

    def test_delitem_changes_state(self):
        self.barterdude["foo"] = foo = Mock()
        self.assertEqual(foo, self.barterdude["foo"])

        del self.barterdude["foo"]
        with self.assertRaises(KeyError):
            self.assertIsNone(self.barterdude["foo"])

    def test_len_returns_state_len(self):
        test_data = {"foo": 1, "bar": 2}
        for k, v in test_data.items():
            self.barterdude[k] = v

        self.assertEqual(
            len(self.barterdude),
            len(dict(self.barterdude._BarterDude__app))
        )

    async def test_iter_iters_through_internal_state_value(self):
        test_data = {"foo": 1, "bar": 2}
        for k, v in test_data.items():
            self.barterdude[k] = v

        state = dict(**self.barterdude)
        self.assertDictContainsSubset(test_data, state)

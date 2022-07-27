from asynctest import TestCase
from barterdude.mocks import PartialMockService, MockWithAssignment
from barterdude.mocks import BarterdudeMock, RabbitMQMessageMock


class Service:

    def __init__(self):
        self.x = 10

    def get_string(self):
        return 'random_string'

    def get_number(self):
        return 42

    async def get_number_async(self):
        return 43


class TestMockWithAssignment(TestCase):

    def test_mock_should_work_with_assignment(self):
        mock = MockWithAssignment()
        mock.any_method(123)
        mock['any_key'] = 'any_value'

        mock.any_method.assert_called_once()
        mock.any_method.assert_called_with(123)
        assert mock['any_key'] == 'any_value'
        assert len(mock) == 1

        for key in mock:
            assert key == 'any_key'

        del mock['any_key']
        assert 'any_key' not in mock

        assert mock.get_calls() == [{
            'method': 'any_method',
            'args': (123,),
            'kwargs': {}
        }]


class TestPartialMockService(TestCase):

    def setUp(self):
        self.service = Service()

    async def test_without_methods(self):
        mock = PartialMockService(self.service, 'service')
        assert mock.get_string() == 'random_string'
        assert mock.x == 10
        assert mock.get_number() == 42
        assert await mock.get_number_async() == 43

    async def test_with_methods(self):
        mock = PartialMockService(
            self.service,
            'service',
            methods={'get_number': 44},
            async_methods={'get_number_async': 45},
        )
        assert mock.get_string() == 'random_string'
        assert mock.x == 10
        assert mock.get_number() == 44
        assert await mock.get_number_async() == 45


class TestRabbitMQMessageMock(TestCase):

    def test_mock_should_have_body_and_headers(self):
        body = {'a': 1}
        headers = {'b': 2}
        mock = RabbitMQMessageMock(body, headers)
        mock.accept()
        mock.reject(requeue=True)
        assert mock.body == body
        assert mock.properties.headers == headers
        mock.accept.assert_called_once()
        mock.reject.assert_called_once()
        mock.reject.assert_called_with(requeue=True)


class TestBarterdudeMock(TestCase):

    def setUp(self):
        self.service = Service()

    async def test_mock_should_have_publish_and_dependencies(self):
        dependencies = [
            PartialMockService(
                self.service,
                'service',
                methods={'get_number': 44},
                async_methods={'get_number_async': 45},
            )
        ]
        payload = {'data': {'a': 1}}
        mock = BarterdudeMock(dependencies)
        mock.publish_amqp(payload)
        mock.publish_amqp.assert_called_once()
        mock.publish_amqp.assert_called_with(payload)
        assert 'service' in mock
        assert mock['service'].get_string() == 'random_string'
        assert mock['service'].get_number() == 44
        assert await mock['service'].get_number_async() == 45

from unittest import TestCase
from barterdude.mocks import BarterdudeMock, RabbitMQMessageMock


class TestMocks(TestCase):

    def test_mock_rabbitmqmessage(self):
        mock = RabbitMQMessageMock({'a': 1}, {'b': 2})
        mock.accept()
        mock.reject(requeue=False)

        assert mock.get_calls() == [
            {
                'method': 'accept',
                'args': (),
                'kwargs': {}
            },
            {
                'method': 'reject',
                'args': (),
                'kwargs': {'requeue': False}
            },
        ]

    async def test_mock_barterdude(self):
        mock = BarterdudeMock()

        mock['value'] = 10
        await mock.publish_amqp(data={'a': 1})

        assert mock['value'] == 10
        assert len(mock) == 1

        for key in mock:
            assert key == 'value'

        del mock['value']
        assert 'value' not in mock

        assert mock.get_calls() == [
            {
                'method': 'publish_amqp',
                'args': (),
                'kwargs': {'data': {'a': 1}}
            },
        ]

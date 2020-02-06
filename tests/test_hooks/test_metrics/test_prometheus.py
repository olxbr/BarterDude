from asynctest import TestCase, Mock, patch
from tests.helpers import get_app

from barterdude.hooks.metrics.prometheus import Prometheus


class TestPrometheus(TestCase):
    @patch("barterdude.hooks.metrics.prometheus.generate_latest")
    async def test_should_call_response_from_prometheus(self, mock):
        mock.return_value = "test prometheus"
        self.app = get_app()
        self.registry = Mock()
        prometheus = Prometheus(
            barterdude=self.app,
            labels={"test": "my_test"},
            path="/metrics",
            registry=self.registry
        )
        response = await prometheus()
        mock.assert_called_once()
        mock.assert_called_with(self.registry)
        self.assertEqual(response.status, 200)
        self.assertEqual(
            response.content_type, "text/plain"
        )
        self.assertEqual(response.charset, "utf-8")
        self.assertEqual(
            response.body._value, bytes(mock.return_value, "utf-8")
        )

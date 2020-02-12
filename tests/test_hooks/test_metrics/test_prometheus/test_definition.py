from asynctest import TestCase, Mock, MagicMock

from barterdude.hooks.metrics.prometheus.definition import Definition
from prometheus_client.metrics import Counter, Histogram


class TestDefinition(TestCase):

    def setUp(self):
        self.metrics = MagicMock()
        self.metric = Mock()
        self.metrics.__getitem__.return_value = self.metric
        self.default_kwargs = {
            "labelnames": ["test"]
        }
        self.definition = Definition(metrics=self.metrics)

    def test_should_prepare_before_consume(self):
        name = "my_metric"
        self.definition.prepare_before_consume(
            name,
            **self.default_kwargs
        )
        self.metrics.__setitem__.assert_called_once()
        mock_call = self.metrics.__setitem__.call_args[0]
        self.assertEqual(mock_call[0], "my_metric")
        self.assertEqual(type(mock_call[1]), Counter)

    def test_should_prepare_on_complete(self):
        name = "my_metric"
        self.definition.prepare_on_complete(
            name,
            **self.default_kwargs
        )
        self.metrics.__setitem__.assert_called_once()
        mock_call = self.metrics.__setitem__.call_args[0]
        self.assertEqual(mock_call[0], "my_metric")
        self.assertEqual(type(mock_call[1]), Counter)

    def test_should_prepare_time_measure(self):
        name = "my_metric"
        self.definition.prepare_time_measure(
            name,
            **self.default_kwargs
        )
        self.metrics.__setitem__.assert_called_once()
        mock_call = self.metrics.__setitem__.call_args[0]
        self.assertEqual(mock_call[0], "my_metric")
        self.assertEqual(type(mock_call[1]), Histogram)

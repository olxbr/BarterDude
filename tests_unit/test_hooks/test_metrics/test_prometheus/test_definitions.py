from asynctest import TestCase, Mock, MagicMock

from barterdude.hooks.metrics.prometheus.definitions import Definitions
from prometheus_client.metrics import Counter, Histogram, REGISTRY


class TestDefinitions(TestCase):

    def setUp(self):
        self.metrics = MagicMock()
        self.metric = Mock()
        self.metrics.__getitem__.return_value = self.metric
        self.definitions = Definitions(
            registry=REGISTRY, metrics=self.metrics, labelkeys=["labelnames"]
        )

    def test_should_prepare_before_consume(self):
        name = "my_metric"
        self.definitions._prepare_before_consume(
            name, "namespace", "unit"
        )
        self.metrics.__setitem__.assert_called_once()
        mock_call = self.metrics.__setitem__.call_args[0]
        self.assertEqual(mock_call[0], "my_metric")
        self.assertEqual(type(mock_call[1]), Counter)

    def test_should_prepare_on_connection_fail(self):
        name = "my_metric"
        self.definitions._prepare_on_connection_fail(
            name, "namespace", "unit"
        )
        self.metrics.__setitem__.assert_called_once()
        mock_call = self.metrics.__setitem__.call_args[0]
        self.assertEqual(mock_call[0], "my_metric")
        self.assertEqual(type(mock_call[1]), Counter)

    def test_should_prepare_histogram_measure(self):
        name = "my_metric"
        self.definitions._prepare_histogram_measure(
            name, "namespace", "unit"
        )
        self.metrics.__setitem__.assert_called_once()
        mock_call = self.metrics.__setitem__.call_args[0]
        self.assertEqual(mock_call[0], "my_metric")
        self.assertEqual(type(mock_call[1]), Histogram)

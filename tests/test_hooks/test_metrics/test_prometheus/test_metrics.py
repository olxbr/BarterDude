from asynctest import TestCase, Mock
from prometheus_client.metrics import MetricWrapperBase

from barterdude.hooks.metrics.prometheus.metrics import Metrics


class TestMetrics(TestCase):
    def test_should_set_and_get_items(self):
        metrics = Metrics()
        metric_mock = Mock(spec=MetricWrapperBase)
        metrics["metric"] = metric_mock
        self.assertEqual(metrics["metric"], metric_mock)

    def test_should_raising_error_setting_duplicate_keys(self):
        metrics = Metrics()
        metric_mock = Mock(spec=MetricWrapperBase)
        metrics["metric"] = metric_mock
        with self.assertRaises(ValueError):
            metrics["metric"] = metric_mock

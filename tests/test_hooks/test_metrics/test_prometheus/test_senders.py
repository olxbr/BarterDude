from asynctest import TestCase, Mock
from prometheus_client.metrics import MetricWrapperBase

from barterdude.hooks.metrics.prometheus.senders import Senders


class TestSenders(TestCase):
    def test_should_set_and_get_items(self):
        senders = Senders()
        metric_mock = Mock(spec=MetricWrapperBase)
        senders["metric"] = metric_mock
        self.assertEqual(senders["metric"], metric_mock)

    def test_should_raising_error_setting_duplicate_keys(self):
        senders = Senders()
        metric_mock = Mock(spec=MetricWrapperBase)
        senders["metric"] = metric_mock
        with self.assertRaises(ValueError):
            senders["metric"] = metric_mock

import freezegun
from asynctest import TestCase, Mock, patch

from barterdude.hooks.metrics.prometheus import Prometheus

from prometheus_client import (
    Counter,
    Gauge,
    Summary,
    Histogram,
    Info,
    Enum
)


class TestPrometheus(TestCase):
    def setUp(self):
        self.app = Mock()
        self.registry = Mock()
        self.labels = {"test": "my_test"}
        self.message = {"message": "test"}
        self.prometheus = Prometheus(
            barterdude=self.app,
            labels=self.labels,
            path="/metrics",
            registry=self.registry,
        )

    @patch("barterdude.hooks.metrics.prometheus.generate_latest")
    async def test_should_call_response_from_prometheus(self, mock):
        mock.return_value = "test prometheus"
        response = await self.prometheus(Mock())
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

    @patch("barterdude.hooks.metrics.prometheus.Prometheus.metrics")
    async def test_should_call_prometheus_on_before_consume(
        self, mock_metric_obj
    ):
        mock_counter_histogram = Mock()
        mock_counter_histogram.observe = Mock()
        mock_labels = Mock()
        mock_labels.labels = Mock(
            return_value=mock_counter_histogram
        )
        mock_metric_obj.__getitem__ = Mock(return_value=mock_labels)
        await self.prometheus.before_consume(self.message)
        mock_labels.labels.assert_called_once()
        mock_labels.labels.assert_called_with(**self.labels)
        mock_counter_histogram.inc.assert_called_once()

    @patch("barterdude.hooks.metrics.prometheus.Prometheus.metrics")
    async def test_should_call_prometheus_on_success(self, mock_metric_obj):
        mock_counter_histogram = Mock()
        mock_counter_histogram.observe = Mock()
        mock_labels = Mock()
        mock_labels.labels = Mock(
            return_value=mock_counter_histogram
        )
        mock_metric_obj.__getitem__ = Mock(return_value=mock_labels)
        await self.prometheus.before_consume(self.message)
        await self.prometheus.on_success(self.message)
        self.assertEqual(mock_labels.labels.call_count, 2)
        mock_labels.labels.assert_called_with(
            error="", state="success", test="my_test"
        )
        self.assertEqual(mock_counter_histogram.inc.call_count, 1)
        mock_counter_histogram.observe.assert_called_once()

    @patch("barterdude.hooks.metrics.prometheus.Prometheus.metrics")
    async def test_should_call_prometheus_on_fail(self, mock_metric_obj):
        mock_counter_histogram = Mock()
        mock_counter_histogram.observe = Mock()
        mock_labels = Mock()
        mock_labels.labels = Mock(
            return_value=mock_counter_histogram
        )
        mock_metric_obj.__getitem__ = Mock(return_value=mock_labels)
        await self.prometheus.before_consume(self.message)
        await self.prometheus.on_fail(self.message, Exception())
        self.assertEqual(mock_labels.labels.call_count, 2)
        mock_labels.labels.assert_called_with(
            error="<class 'Exception'>", state="fail", test="my_test"
        )
        self.assertEqual(mock_counter_histogram.inc.call_count, 1)
        mock_counter_histogram.observe.assert_called_once()

    @patch("barterdude.hooks.metrics.prometheus.Prometheus.metrics")
    async def test_should_measure_time_on_success(self, mock_metric_obj):
        mock_histogram = Mock()
        mock_histogram.observe = Mock()
        mock_labels = Mock()
        mock_labels.labels = Mock(
            return_value=mock_histogram
        )
        mock_metric_obj.__getitem__ = Mock(return_value=mock_labels)
        with freezegun.freeze_time() as freeze:
            await self.prometheus.before_consume(self.message)
            freeze.tick()
            await self.prometheus.on_success(self.message)
        mock_histogram.observe.assert_called_once()
        mock_histogram.observe.assert_called_with(1.0)

    @patch("barterdude.hooks.metrics.prometheus.Prometheus.metrics")
    async def test_should_measure_time_on_fail(self, mock_metric_obj):
        mock_histogram = Mock()
        mock_histogram.observe = Mock()
        mock_labels = Mock()
        mock_labels.labels = Mock(
            return_value=mock_histogram
        )
        mock_metric_obj.__getitem__ = Mock(return_value=mock_labels)
        with freezegun.freeze_time() as freeze:
            await self.prometheus.before_consume(self.message)
            freeze.tick()
            await self.prometheus.on_fail(self.message, Exception())
        mock_histogram.observe.assert_called_once()
        mock_histogram.observe.assert_called_with(1.0)

    @patch("barterdude.hooks.metrics.prometheus.Metrics")
    async def test_should_remove_message_from_timer_on_complete(
        self, mock_metric_class
    ):
        await self.prometheus.before_consume(self.message)
        self.assertEqual(len(self.prometheus._msg_start), 1)
        await self.prometheus._on_complete(
            self.message, "success", Exception()
        )
        self.assertDictEqual(
            self.prometheus._msg_start,
            {}
        )

    @patch("barterdude.hooks.metrics.prometheus.Prometheus.metrics")
    async def test_should_increment_on_connection_fail_counter(self, metrics):
        counter = Mock()
        labels = Mock(labels=Mock(return_value=counter))
        metrics.__getitem__ = Mock(return_value=labels)
        await self.prometheus.on_connection_fail(Mock(), Mock())
        self.assertEqual(labels.labels.call_count, 1)
        labels.labels.assert_called_with(test='my_test')
        counter.inc.assert_called_once()

    def test_should_call_counter(self):
        self.assertTrue(
            isinstance(self.prometheus.metrics.counter(
                name="test", documentation="doc"
            ), Counter)
        )

    def test_should_call_gauge(self):
        self.assertTrue(
            isinstance(self.prometheus.metrics.gauge(
                name="test", documentation="doc"
            ), Gauge)
        )

    def test_should_call_summary(self):
        self.assertTrue(
            isinstance(self.prometheus.metrics.summary(
                name="test", documentation="doc"
            ), Summary)
        )

    def test_should_call_histogram(self):
        self.assertTrue(
            isinstance(self.prometheus.metrics.histogram(
                name="test", documentation="doc"
            ), Histogram)
        )

    def test_should_call_info(self):
        self.assertTrue(
            isinstance(self.prometheus.metrics.info(
                name="test", documentation="doc"
            ), Info)
        )

    def test_should_call_enum(self):
        self.assertTrue(
            isinstance(self.prometheus.metrics.enum(
                name="test", documentation="doc", states=Mock()
            ), Enum)
        )

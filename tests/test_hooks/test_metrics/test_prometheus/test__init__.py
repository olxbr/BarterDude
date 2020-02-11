import freezegun
from asynctest import TestCase, MagicMock, Mock, patch

from barterdude.hooks.metrics.prometheus import Prometheus
from barterdude.hooks.metrics.prometheus.definition import Definition


class TestPrometheus(TestCase):
    def setUp(self):
        self.app = Mock()
        self.registry = Mock()
        self.metrics = MagicMock()
        self.mock_metric = Mock()
        self.metrics.__getitem__.return_value = self.mock_metric
        self.definition = Definition(metrics=self.metrics)
        self.definition.get_metric = Mock(return_value=self.mock_metric)
        self.labels = {"test": "my_test"}
        self.message = {"message": "test"}
        self.prometheus = Prometheus(
            barterdude=self.app,
            labels=self.labels,
            path="/metrics",
            registry=self.registry,
            definition=self.definition
        )

    @patch("barterdude.hooks.metrics.prometheus.generate_latest")
    async def test_should_call_response_from_prometheus(self, mock):
        mock.return_value = "test prometheus"
        response = await self.prometheus()
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

    async def test_should_call_prometheus_on_before_consume(self):
        mock_count = Mock()
        mock_count.inc = Mock()
        self.mock_metric.labels = Mock(
            return_value=mock_count
        )
        await self.prometheus.before_consume(self.message)
        self.mock_metric.labels.assert_called_once()
        self.mock_metric.labels.assert_called_with(**self.labels)
        mock_count.inc.assert_called_once()

    async def test_should_call_prometheus_on_success(self):
        mock_metric = Mock()
        mock_metric.inc = Mock()
        mock_metric.observe = Mock()
        self.mock_metric.labels = Mock(
            return_value=mock_metric
        )
        await self.prometheus.before_consume(self.message)
        await self.prometheus.on_success(self.message)
        self.assertEqual(self.mock_metric.labels.call_count, 3)
        self.mock_metric.labels.assert_called_with(
            error=None, state='success', test='my_test'
        )
        self.assertEqual(mock_metric.inc.call_count, 2)
        mock_metric.observe.assert_called_once()

    async def test_should_call_prometheus_on_fail(self):
        mock_metric = Mock()
        mock_metric.inc = Mock()
        mock_metric.observe = Mock()
        self.mock_metric.labels = Mock(
            return_value=mock_metric
        )
        await self.prometheus.before_consume(self.message)
        await self.prometheus.on_fail(self.message, Exception())
        self.assertEqual(self.mock_metric.labels.call_count, 3)
        self.mock_metric.labels.assert_called_with(
            error="<class 'Exception'>", state='fail', test='my_test'
        )
        self.assertEqual(mock_metric.inc.call_count, 2)
        mock_metric.observe.assert_called_once()

    async def test_should_measure_time_on_success(self):
        mock_metric = Mock()
        mock_metric.inc = Mock()
        mock_metric.observe = Mock()
        self.mock_metric.labels = Mock(
            return_value=mock_metric
        )
        with freezegun.freeze_time() as freeze:
            await self.prometheus.before_consume(self.message)
            freeze.tick()
            await self.prometheus.on_success(self.message)
        mock_metric.observe.assert_called_once()
        mock_metric.observe.assert_called_with(1.0)

    async def test_should_measure_time_on_fail(self):
        mock_metric = Mock()
        mock_metric.inc = Mock()
        mock_metric.observe = Mock()
        self.mock_metric.labels = Mock(
            return_value=mock_metric
        )
        with freezegun.freeze_time() as freeze:
            await self.prometheus.before_consume(self.message)
            freeze.tick()
            await self.prometheus.on_fail(self.message, Exception())
        mock_metric.observe.assert_called_once()
        mock_metric.observe.assert_called_with(1.0)

    async def test_should_remove_message_from_timer_on_complete(self):
        mock_metric = Mock()
        mock_metric.inc = Mock()
        mock_metric.observe = Mock()
        self.mock_metric.labels = Mock(
            return_value=mock_metric
        )
        await self.prometheus.before_consume(self.message)
        self.assertEqual(len(self.prometheus._msg_start), 1)
        await self.prometheus._on_complete(
            self.message, "my_state", Exception()
        )
        self.assertDictEqual(
            self.prometheus._msg_start,
            {}
        )

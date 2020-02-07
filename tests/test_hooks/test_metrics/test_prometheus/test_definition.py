from asynctest import TestCase, Mock, MagicMock

from barterdude.hooks.metrics.prometheus.definition import Definition
from prometheus_client.metrics import Counter, Histogram


class TestDefinition(TestCase):

    def setUp(self):
        self.senders = MagicMock()
        self.sender = Mock()
        self.senders.__getitem__.return_value = self.sender
        self.default_kwargs = {
            "labelnames": ["test"]
        }
        self.definition = Definition(senders=self.senders)

    def test_should_prepare_before_consume(self):
        name = "my_metric"
        before_args_len = len(self.default_kwargs)
        before_labels_len = len(self.default_kwargs["labelnames"])
        self.definition.prepare_before_consume(
            name,
            self.default_kwargs
        )
        after_args_len = len(self.default_kwargs)
        after_labels_len = len(self.default_kwargs["labelnames"])
        self.assertEqual(before_args_len, after_args_len)
        self.assertEqual(before_labels_len, after_labels_len)
        self.senders.__setitem__.assert_called_once()
        mock_call = self.senders.__setitem__.call_args[0]
        self.assertEqual(mock_call[0], "my_metric")
        self.assertEqual(type(mock_call[1]), Counter)

    def test_should_prepare_on_complete(self):
        name = "my_metric"
        before_args_len = len(self.default_kwargs)
        before_labels_len = len(self.default_kwargs["labelnames"])
        self.definition.prepare_on_complete(
            name,
            self.default_kwargs
        )
        after_args_len = len(self.default_kwargs)
        after_labels_len = len(self.default_kwargs["labelnames"])
        self.assertEqual(before_args_len, after_args_len)
        self.assertEqual(before_labels_len + 2, after_labels_len)
        self.senders.__setitem__.assert_called_once()
        mock_call = self.senders.__setitem__.call_args[0]
        self.assertEqual(mock_call[0], "my_metric")
        self.assertEqual(type(mock_call[1]), Counter)

    def test_should_prepare_time_measure(self):
        name = "my_metric"
        before_args_len = len(self.default_kwargs)
        before_labels_len = len(self.default_kwargs["labelnames"])
        self.definition.prepare_time_measure(
            name,
            self.default_kwargs
        )
        after_args_len = len(self.default_kwargs)
        after_labels_len = len(self.default_kwargs["labelnames"])
        self.assertEqual(before_args_len + 1, after_args_len)
        self.assertEqual(before_labels_len + 2, after_labels_len)
        self.senders.__setitem__.assert_called_once()
        mock_call = self.senders.__setitem__.call_args[0]
        self.assertEqual(mock_call[0], "my_metric")
        self.assertEqual(type(mock_call[1]), Histogram)

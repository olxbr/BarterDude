from unittest import TestCase
from barterdude.hooks.metrics.prometheus.partial_metric import partial_metric


class TestMetric():
    def __init__(self, registry):
        self.registry = registry


class TestPartialMetric(TestCase):

    def test_should_partial_metric_with_registry(self):
        registry = "my little registry"
        new_klass = partial_metric(TestMetric, registry)
        self.assertTrue(isinstance(new_klass(), TestMetric))
        self.assertEqual(new_klass().registry, registry)

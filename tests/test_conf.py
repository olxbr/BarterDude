import logging
from pythonjsonlogger import jsonlogger

from asynctest import TestCase
from barterdude.conf import getLogger


class TestConf(TestCase):

    def setUp(self):
        self.log_name = "barterdude"
        self.log_level = logging.INFO

    async def test_should_get_log_with_default_configs(self):
        logger = getLogger()
        self.assertEqual(
            type(logger.handlers[0]),
            logging.StreamHandler
        )
        self.assertEqual(logger.name, self.log_name)
        self.assertEqual(logger.level, self.log_level)
        self.assertEqual(
            type(logger.handlers[0].formatter),
            jsonlogger.JsonFormatter
        )

    async def test_should_get_log_with_custom_configs(self):
        logger = getLogger("test_log", logging.DEBUG)
        self.assertEqual(
            type(logger.handlers[0]),
            logging.StreamHandler
        )
        self.assertEqual(logger.name, "test_log")
        self.assertEqual(logger.level, logging.DEBUG)
        self.assertEqual(
            type(logger.handlers[0].formatter),
            jsonlogger.JsonFormatter
        )

    async def test_should_get_log_with_custom_configs_even_called_after(self):
        logger_first = getLogger()
        logger = getLogger("test_log", logging.DEBUG)
        self.assertEqual(
            type(logger.handlers[0]),
            logging.StreamHandler
        )
        self.assertEqual(logger_first.name, self.log_name)
        self.assertEqual(logger_first.level, self.log_level)
        self.assertEqual(logger.name, "test_log")
        self.assertEqual(logger.level, logging.DEBUG)
        self.assertEqual(
            type(logger.handlers[0].formatter),
            jsonlogger.JsonFormatter
        )
        self.assertEqual(len(logger_first.handlers), 1)
        self.assertEqual(len(logger.handlers), 1)

from traceback import format_tb
from asynctest import TestCase, Mock, patch
from barterdude.hooks.logging import Logging


class TestLogging(TestCase):
    @patch("barterdude.hooks.logging.getLogger")
    def setUp(self, getLogger):
        self.message = Mock()
        self.message.body = {
            "senderAccountId": "32074499",
            "messageTimestamp": "2019-12-26T19:35:10.049Z",
            "chatId": "691645593-18833924-32074499"
        }
        self.logger = getLogger.return_value
        self.logging = Logging()

    async def test_should_log_before_consume(self):
        await self.logging.before_consume(self.message)
        self.logger.info.assert_called_once()
        self.logger.info.assert_called_with(
            f"going to consume message: {self.message.body}"
        )

    async def test_should_log_on_success(self):
        await self.logging.on_success(self.message)
        self.logger.info.assert_called_once()
        self.logger.info.assert_called_with(
            f"successfully consumed message: {self.message.body}"
        )

    async def test_should_log_on_fail(self):
        error = KeyError('key not find')
        tb = format_tb(error.__traceback__)
        await self.logging.on_fail(self.message, error)
        self.logger.error.assert_called_once()
        self.logger.error.assert_called_with(
            f"failed to consume message: {self.message.body}\n"
            f"{repr(error)}\n{tb}"
        )

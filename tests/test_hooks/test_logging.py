from asynctest import TestCase, Mock
from barterdude.hooks.logging import Logging


class TestLogging(TestCase):
    def setUp(self):
        self.message = {
            "senderAccountId": "32074499",
            "messageTimestamp": "2019-12-26T19:35:10.049Z",
            "chatId": "691645593-18833924-32074499"
        }
        self.logger = Mock()
        self.logging = Logging(self.logger)

    async def test_should_log_before_consume(self):
        await self.logging.before_consume(self.message)
        self.logger.info.assert_called_once()
        self.logger.info.assert_called_with(
            f"going to consume message: {self.message}"
        )

    async def test_should_log_on_success(self):
        await self.logging.on_success(self.message)
        self.logger.info.assert_called_once()
        self.logger.info.assert_called_with(
            f"successfully consumed message: {self.message}"
        )

    async def test_should_log_on_fail(self):
        await self.logging.on_fail(self.message, KeyError('key not find'))
        error = "KeyError('key not find')"
        self.logger.error.assert_called_once()
        self.logger.error.assert_called_with(
            f"failed to consume message ({error}): {self.message}"
        )

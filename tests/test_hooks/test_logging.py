from asynctest import TestCase, patch
from barterdude.hooks.logging import Logging


class TestLogging(TestCase):
    def setUp(self):
        self.message = {
            "senderAccountId": "32074499",
            "messageTimestamp": "2019-12-26T19:35:10.049Z",
            "chatId": "691645593-18833924-32074499"
        }
        self.logging = Logging()

    @patch("barterdude.hooks.logging.logging.info")
    async def test_should_log_before_consume(self, mock):
        await self.logging.before_consume(self.message)
        mock.assert_called_once()
        mock.assert_called_with(f"going to consume message: {self.message}")

    @patch("barterdude.hooks.logging.logging.info")
    async def test_should_log_on_success(self, mock):
        await self.logging.on_success(self.message)
        mock.assert_called_once()
        mock.assert_called_with(
            f"successfully consumed message: {self.message}"
        )

    @patch("barterdude.hooks.logging.logging.error")
    async def test_should_log_on_fail(self, mock):
        error = "KeyError"
        await self.logging.on_fail(self.message, error)
        mock.assert_called_once()
        mock.assert_called_with(
            f"failed to consume message ({error}): {self.message}"
        )

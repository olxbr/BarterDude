import unittest
from unittest.mock import MagicMock

from kombu import Message as KombuMessage

from barterdude.message import Message


class TestMessage(unittest.TestCase):
    def setUp(self):
        self.body_dict = {"result": "my body, my rules"}
        self.body = """
            {"result": "my body, my rules"}
        """

    def test_should_returns_message_as_dict(self):
        k_message = KombuMessage(self.body, content_type="application/json")

        message = Message(self.body, k_message)
        self.assertDictEqual(
            message.parse_content_type(),
            self.body_dict
        )

    def test_should_returns_message_as_string(self):
        k_message = KombuMessage(self.body, content_type="application/json")

        message = Message(self.body, k_message)
        self.assertEqual(
            message.as_string(),
            self.body
        )

    def test_should_returns_message_as_string_without_content_type(self):
        k_message = KombuMessage(self.body)

        message = Message(self.body, k_message)
        self.assertEqual(
            message.parse_content_type(),
            self.body
        )

    def test_should_call_ack_on_kombu_message(self):
        k_message = KombuMessage(self.body)
        k_message.ack = MagicMock()

        message = Message(self.body, k_message)
        k_message.ack.assert_not_called()
        message.ack()
        k_message.ack.assert_called_once()

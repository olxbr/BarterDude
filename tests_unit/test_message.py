from asynctest import TestCase, Mock
from asyncworker.rabbitmq.message import RabbitMQMessage
from barterdude.message import (
    Message, MessageValidation, ValidationException)
from tests_unit.helpers import load_fixture


class TestMessage(TestCase):
    def test_should_convert_rabbitmq_message_to_message(self):
        rbmq_message = RabbitMQMessage(1, Mock())
        message = Message(rbmq_message)
        self.assertEqual(message.body, rbmq_message.body)
        self.assertEqual(
            message.properties, rbmq_message._amqp_message._properties)
        self.assertEqual(
            message.queue_name, rbmq_message._amqp_message.queue_name)
        self.assertEqual(message.raw, rbmq_message.serialized_data)

    async def test_should_call_rbmq_methods(self):
        rbmq_message = Mock(RabbitMQMessage)
        message = Message(rbmq_message)
        message.reject()
        rbmq_message.reject.assert_called_once_with(True)
        rbmq_message.reset_mock()
        message.reject(False)
        rbmq_message.reject.assert_called_once_with(False)
        rbmq_message.reset_mock()
        message.accept()
        rbmq_message.accept.assert_called_once_with()
        rbmq_message.reset_mock()
        await message.process_success()
        rbmq_message.process_success.assert_awaited_with()
        rbmq_message.reset_mock()
        await message.process_exception()
        rbmq_message.process_exception.assert_awaited_with()

    def test_should_work_with_dict(self):
        test_message = {"key": "value"}
        rbmq_message = Mock(RabbitMQMessage)
        rbmq_message.body = test_message
        message = Message(rbmq_message)
        self.assertEqual(message.body, test_message)

    def test_should_work_with_no_dict(self):
        test_message = "value"
        rbmq_message = Mock(RabbitMQMessage)
        rbmq_message.body = test_message
        message = Message(rbmq_message)
        self.assertEqual(message.body, test_message)


class TestMessageValidation(TestCase):
    def setUp(self):
        self.schema = load_fixture("schema.json")
        self.rbmq_message = Mock(RabbitMQMessage)

    def test_should_return_without_validation_even_wrong(self):
        self.rbmq_message.body = {"wrong": "key"}
        validation = MessageValidation()
        message = validation(self.rbmq_message)
        validation.validate(message)
        self.assertEqual(self.rbmq_message.body, message.body)

    def test_should_return_message_with_validation(self):
        self.rbmq_message.body = {"key": "ok"}
        validation = MessageValidation(self.schema)
        message = validation(self.rbmq_message)
        validation.validate(message)
        self.assertEqual(self.rbmq_message.body, message.body)

    def test_should_raise_error_with_wrong_message(self):
        self.rbmq_message.body = {"wrong": "key"}
        validation = MessageValidation(self.schema)
        with self.assertRaises(ValidationException):
            validation(self.rbmq_message)
        with self.assertRaises(ValidationException):
            validation.validate(self.rbmq_message)

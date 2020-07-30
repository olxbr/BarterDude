from asynctest import TestCase, Mock
from barterdude.hooks.schema_validation import SchemaValidation
from barterdude.message import Message
from barterdude.exceptions import StopFailFlowException
from tests_unit.helpers import load_fixture


class TestSchemaValidation(TestCase):
    def setUp(self):
        self.schema = load_fixture("schema.json")
        self.rbmq_message = Mock(Message)

    async def test_should_run_without_validation_even_wrong(self):
        self.rbmq_message.body = {"wrong": "key"}
        validation = SchemaValidation()
        try:
            await validation.before_consume(self.rbmq_message)
        except Exception:
            self.fail()

    async def test_should_run_message_with_validation(self):
        self.rbmq_message.body = {"key": "ok"}
        validation = SchemaValidation(self.schema)
        try:
            await validation.before_consume(self.rbmq_message)
        except Exception:
            self.fail()

    async def test_should_raise_error_with_wrong_message(self):
        self.rbmq_message.body = {"wrong": "key"}
        validation = SchemaValidation(self.schema)
        with self.assertRaises(StopFailFlowException):
            await validation.before_consume(self.rbmq_message)

    async def test_should_fail_with_requeue(self):
        validation = SchemaValidation(requeue_on_fail=True)
        await validation.on_fail(self.rbmq_message, Exception())
        self.rbmq_message.reject.assert_called_once_with(True)

    async def test_should_fail_without_requeue(self):
        validation = SchemaValidation(requeue_on_fail=False)
        await validation.on_fail(self.rbmq_message, Exception())
        self.rbmq_message.reject.assert_called_once_with(False)

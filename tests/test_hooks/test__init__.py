from asynctest import TestCase, Mock
from barterdude.hooks import HttpHook


class TestHttpHook(TestCase):
    def setUp(self):
        self.app = Mock()

    def test_should_call_http_route_from_hook(self):
        hook = HttpHook(
            self.app,
            "/my_little_route"
        )
        self.app.add_endpoint.assert_called_once()
        self.app.add_endpoint.assert_called_with(
            routes=["/my_little_route"],
            methods=["GET"],
            hook=hook.__call__
        )

    async def test_should_fail_when_calling_unimplemented_methods(self):
        hook = HttpHook(
            self.app,
            "/my_little_route"
        )
        with self.assertRaises(NotImplementedError):
            await hook(Mock())
        with self.assertRaises(NotImplementedError):
            await hook.before_consume(None)
        with self.assertRaises(NotImplementedError):
            await hook.on_success(None)
        with self.assertRaises(NotImplementedError):
            await hook.on_fail(None, None)
        with self.assertRaises(NotImplementedError):
            await hook.on_connection_fail(None, None)

from asynctest import TestCase, Mock
from tests.helpers import get_app

from asyncworker import RouteTypes
from barterdude.hooks import HttpHook


class TestHttpHook(TestCase):
    def setUp(self):
        self.app = get_app()

    def test_should_call_http_route_from_hook(self):
        self.app.route = Mock()
        HttpHook(
            self.app,
            "/my_little_route"
        )
        self.app.route.assert_called_once()
        self.app.route.assert_called_with(
            routes=["/my_little_route"],
            methods=["GET"],
            type=RouteTypes.HTTP
        )

    async def test_should_fail_when_calling_unimplemented_methods(self):
        hook = HttpHook(
            self.app,
            "/my_little_route"
        )
        with self.assertRaises(NotImplementedError):
            await hook()
        with self.assertRaises(NotImplementedError):
            await hook.before_consume(None)
        with self.assertRaises(NotImplementedError):
            await hook.on_success(None)
        with self.assertRaises(NotImplementedError):
            await hook.on_fail(None, None)

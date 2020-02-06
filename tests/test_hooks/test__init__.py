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

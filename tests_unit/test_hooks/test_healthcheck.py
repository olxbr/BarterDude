from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock
from freezegun import freeze_time
from barterdude.hooks.healthcheck import Healthcheck, HealthcheckMonitored


class HealthcheckMonitoredMock(HealthcheckMonitored):
    def __init__(self, healthy=True):
        self.healthy = healthy

    def healthcheck(self):
        return self.healthy


@freeze_time()
class TestHealthcheck(IsolatedAsyncioTestCase):
    maxDiff = None

    def setUp(self):
        self.success_rate = 0.9
        self.health_window = 60.0
        self.app = MagicMock()
        self.monitoredModules = {}
        self.app.__iter__.side_effect = lambda: iter(self.monitoredModules)
        self.app.__getitem__.side_effect = (
            lambda module: self.monitoredModules[module]
        )
        self.healthcheck = Healthcheck(
            self.app,
            "/healthcheck",
            self.success_rate,
            self.health_window
        )

    async def test_should_call_before_consume(self):
        await self.healthcheck.before_consume(None)

    async def test_should_pass_healthcheck_when_no_messages(self):
        response = await self.healthcheck(self.app)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.content_type, "text/plain")
        self.assertEqual(
            response.body._value.decode('utf-8'),
            '{"message": "No messages in last 60.0s", "status": "ok"}'
        )

    async def test_should_pass_healthcheck_when_only_sucess(self):
        await self.healthcheck.on_success(None)
        response = await self.healthcheck(self.app)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.content_type, "text/plain")
        self.assertEqual(
            response.body._value.decode('utf-8'),
            '{"message": "Success rate: 1.0 (expected: 0.9)", '
            '"fail": 0, "success": 1, "status": "ok"}'
        )

    async def test_should_pass_healthcheck_when_success_rate_is_high(self):
        await self.healthcheck.on_fail(None, None)
        for i in range(0, 9):
            await self.healthcheck.on_success(None)
        response = await self.healthcheck(self.app)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.content_type, "text/plain")
        self.assertEqual(
            response.body._value.decode('utf-8'),
            '{"message": "Success rate: 0.9 (expected: 0.9)", '
            '"fail": 1, "success": 9, "status": "ok"}'
        )

    async def test_should_fail_healthcheck_when_only_fail(self):
        await self.healthcheck.on_fail(None, None)
        response = await self.healthcheck(self.app)
        self.assertEqual(response.status, 500)
        self.assertEqual(response.content_type, "text/plain")
        self.assertEqual(
            response.body._value.decode('utf-8'),
            '{"message": "Success rate: 0.0 (expected: 0.9)", '
            '"fail": 1, "success": 0, "status": "fail"}'
        )

    async def test_should_fail_healthcheck_when_success_rate_is_low(self):
        await self.healthcheck.on_success(None)
        await self.healthcheck.on_fail(None, None)
        response = await self.healthcheck(self.app)
        self.assertEqual(response.status, 500)
        self.assertEqual(response.content_type, "text/plain")
        self.assertEqual(
            response.body._value.decode('utf-8'),
            '{"message": "Success rate: 0.5 (expected: 0.9)", '
            '"fail": 1, "success": 1, "status": "fail"}'
        )

    async def test_should_fail_when_force_fail_is_called(self):
        self.healthcheck.force_fail()
        await self.healthcheck.on_success(None)
        response = await self.healthcheck(self.app)
        self.assertEqual(response.status, 500)
        self.assertEqual(response.content_type, "text/plain")
        self.assertEqual(
            response.body._value.decode('utf-8'),
            '{"message": "Healthcheck fail called manually", "status": "fail"}'
        )

    async def test_should_erase_old_messages(self):
        tick = 7
        with freeze_time(auto_tick_seconds=tick):
            for i in range(0, 10):
                await self.healthcheck.on_fail(None, None)
            await self.healthcheck.on_success(None)
            response = await self.healthcheck(self.app)
            self.assertEqual(
                response.body._value.decode('utf-8'),
                '{"message": "Success rate: 0.125 (expected: 0.9)", '
                '"fail": 7, "success": 1, "status": "fail"}'
            )

    async def test_should_fail_healthcheck_when_fail_to_connect(self):
        await self.healthcheck.on_connection_fail(None, 3)
        response = await self.healthcheck(self.app)
        self.assertEqual(
            response.body._value.decode('utf-8'),
            '{"message": "Reached max connection fails (3)", "status": "fail"}'
        )

    async def test_should_pass_when_has_one_healthy_monitored_module(self):
        self.monitoredModules = {
            "testModule": HealthcheckMonitoredMock(True)
        }
        response = await self.healthcheck(self.app)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.content_type, "text/plain")
        self.assertEqual(
            response.body._value.decode('utf-8'),
            '{"testModule": "ok", '
            '"message": "No messages in last 60.0s", "status": "ok"}'
        )

    async def test_should_pass_when_has_two_healthy_monitored_module(self):
        self.monitoredModules = {
            "testModule1": HealthcheckMonitoredMock(True),
            "testModule2": HealthcheckMonitoredMock(True)
        }
        response = await self.healthcheck(self.app)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.content_type, "text/plain")
        self.assertEqual(
            response.body._value.decode('utf-8'),
            '{"testModule1": "ok", "testModule2": "ok", '
            '"message": "No messages in last 60.0s", "status": "ok"}'
        )

    async def test_should_fail_when_has_one_failing_monitored_module(self):
        self.monitoredModules = {
            "testModule": HealthcheckMonitoredMock(False)
        }
        response = await self.healthcheck(self.app)
        self.assertEqual(response.status, 500)
        self.assertEqual(response.content_type, "text/plain")
        self.assertEqual(
            response.body._value.decode('utf-8'),
            '{"testModule": "fail", '
            '"message": "No messages in last 60.0s", "status": "fail"}'
        )

    async def test_should_fail_when_has_two_failing_monitored_module(self):
        self.monitoredModules = {
            "testModule1": HealthcheckMonitoredMock(False),
            "testModule2": HealthcheckMonitoredMock(False)
        }
        response = await self.healthcheck(self.app)
        self.assertEqual(response.status, 500)
        self.assertEqual(response.content_type, "text/plain")
        self.assertEqual(
            response.body._value.decode('utf-8'),
            '{"testModule1": "fail", "testModule2": "fail", '
            '"message": "No messages in last 60.0s", "status": "fail"}'
        )

    async def test_should_fail_when_has_failing_and_healthy_modules(self):
        self.monitoredModules = {
            "testModule1": HealthcheckMonitoredMock(False),
            "testModule2": HealthcheckMonitoredMock(True)
        }
        response = await self.healthcheck(self.app)
        self.assertEqual(response.status, 500)
        self.assertEqual(response.content_type, "text/plain")
        self.assertEqual(
            response.body._value.decode('utf-8'),
            '{"testModule1": "fail", "testModule2": "ok", '
            '"message": "No messages in last 60.0s", "status": "fail"}'
        )

    async def test_should_pass_when_has_one_healthy_module_and_messages(self):
        self.monitoredModules = {
            "testModule": HealthcheckMonitoredMock(True)
        }
        await self.healthcheck.on_success(None)
        response = await self.healthcheck(self.app)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.content_type, "text/plain")
        self.assertEqual(
            response.body._value.decode('utf-8'),
            '{"testModule": "ok", '
            '"message": "Success rate: 1.0 (expected: 0.9)", '
            '"fail": 0, "success": 1, "status": "ok"}'
        )

    async def test_should_pass_when_has_one_failing_module_and_messages(self):
        self.monitoredModules = {
            "testModule": HealthcheckMonitoredMock(False)
        }
        await self.healthcheck.on_success(None)
        response = await self.healthcheck(self.app)
        self.assertEqual(response.status, 500)
        self.assertEqual(response.content_type, "text/plain")
        self.assertEqual(
            response.body._value.decode('utf-8'),
            '{"testModule": "fail", '
            '"message": "Success rate: 1.0 (expected: 0.9)", '
            '"fail": 0, "success": 1, "status": "fail"}'
        )

    async def test_should_pass_healthcheck_when_has_simple_module(self):
        self.monitoredModules = {
            "testModule": MagicMock()
        }
        await self.healthcheck.on_success(None)
        response = await self.healthcheck(self.app)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.content_type, "text/plain")
        self.assertEqual(
            response.body._value.decode('utf-8'),
            '{"message": "Success rate: 1.0 (expected: 0.9)", '
            '"fail": 0, "success": 1, "status": "ok"}'
        )

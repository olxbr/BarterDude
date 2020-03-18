from asynctest import TestCase, Mock
from freezegun import freeze_time
from barterdude.hooks.healthcheck import Healthcheck


@freeze_time()
class TestHealthcheck(TestCase):
    maxDiff = None

    def setUp(self):
        self.success_rate = 0.9
        self.health_window = 60.0
        self.healthcheck = Healthcheck(
            Mock(),
            "/healthcheck",
            self.success_rate,
            self.health_window
        )

    async def test_should_call_before_consume(self):
        await self.healthcheck.before_consume(None)

    async def test_should_pass_healthcheck_when_no_messages(self):
        response = await self.healthcheck(Mock())
        self.assertEqual(response.status, 200)
        self.assertEqual(response.content_type, "text/plain")
        self.assertEqual(
            response.body._value.decode('utf-8'),
            '{"message": "No messages in last 60.0s", "status": "ok"}'
        )

    async def test_should_pass_healthcheck_when_only_sucess(self):
        await self.healthcheck.on_success(None)
        response = await self.healthcheck(Mock())
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
        response = await self.healthcheck(Mock())
        self.assertEqual(response.status, 200)
        self.assertEqual(response.content_type, "text/plain")
        self.assertEqual(
            response.body._value.decode('utf-8'),
            '{"message": "Success rate: 0.9 (expected: 0.9)", '
            '"fail": 1, "success": 9, "status": "ok"}'
        )

    async def test_should_fail_healthcheck_when_only_fail(self):
        await self.healthcheck.on_fail(None, None)
        response = await self.healthcheck(Mock())
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
        response = await self.healthcheck(Mock())
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
        response = await self.healthcheck(Mock())
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
            response = await self.healthcheck(Mock())
            self.assertEqual(
                response.body._value.decode('utf-8'),
                '{"message": "Success rate: 0.125 (expected: 0.9)", '
                '"fail": 7, "success": 1, "status": "fail"}'
            )

    async def test_should_fail_healthcheck_when_fail_to_connect(self):
        await self.healthcheck.on_connection_fail(None, 3)
        response = await self.healthcheck(Mock())
        self.assertEqual(
            response.body._value.decode('utf-8'),
            '{"message": "Reached max connection fails (3)", "status": "fail"}'
        )

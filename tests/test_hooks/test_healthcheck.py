from asynctest import TestCase, Mock
from freezegun import freeze_time
from barterdude.hooks.healthcheck import Healthcheck


@freeze_time()
class TestHealthcheck(TestCase):
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
        self.assertEqual(response.body._value, b"No messages until now")

    async def test_should_pass_healthcheck_when_only_sucess(self):
        await self.healthcheck.on_success(None)
        response = await self.healthcheck(Mock())
        self.assertEqual(response.status, 200)
        self.assertEqual(response.content_type, "text/plain")
        self.assertEqual(
            response.body._value,
            b"Bater like a pro! Success rate: 1.0"
        )

    async def test_should_pass_healthcheck_when_success_rate_is_high(self):
        await self.healthcheck.on_fail(None, None)
        for i in range(0, 9):
            await self.healthcheck.on_success(None)
        response = await self.healthcheck(Mock())
        self.assertEqual(response.status, 200)
        self.assertEqual(response.content_type, "text/plain")
        self.assertEqual(
            response.body._value,
            b"Bater like a pro! Success rate: 0.9"
        )

    async def test_should_fail_healthcheck_when_only_fail(self):
        await self.healthcheck.on_fail(None, None)
        response = await self.healthcheck(Mock())
        self.assertEqual(response.status, 500)
        self.assertEqual(response.content_type, "text/plain")
        self.assertEqual(
            response.body._value,
            bytes(f"Success rate 0.0 bellow {self.success_rate}", "utf-8")
        )

    async def test_should_fail_healthcheck_when_success_rate_is_low(self):
        await self.healthcheck.on_success(None)
        await self.healthcheck.on_fail(None, None)
        response = await self.healthcheck(Mock())
        self.assertEqual(response.status, 500)
        self.assertEqual(response.content_type, "text/plain")
        self.assertEqual(
            response.body._value,
            bytes(f"Success rate 0.5 bellow {self.success_rate}", "utf-8")
        )

    async def test_should_fail_when_force_fail_is_called(self):
        self.healthcheck.force_fail()
        await self.healthcheck.on_success(None)
        response = await self.healthcheck(Mock())
        self.assertEqual(response.status, 500)
        self.assertEqual(response.content_type, "text/plain")
        self.assertEqual(
            response.body._value,
            b"Healthcheck fail called manually"
        )

    async def test_should_erase_old_messages(self):
        tick = 7
        with freeze_time(auto_tick_seconds=tick):
            for i in range(0, 10):
                await self.healthcheck.on_fail(None, None)
            await self.healthcheck.on_success(None)
            response = await self.healthcheck(Mock())
            rate = 1 / (1 + (self.health_window - tick) // tick)
            self.assertEqual(
                response.body._value,
                bytes(
                    f"Success rate {rate} bellow {self.success_rate}",
                    "utf-8"
                )
            )

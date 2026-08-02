import asyncio
import time

import pytest

from core.proactive import Alert, BaseMonitor, ProactiveMonitor


class TestAlert:
    def test_default_values(self):
        a = Alert(type="test", title="Test", description="Desc")
        assert a.severity == "info"
        assert a.action_label is None
        assert a.timestamp > 0

    def test_to_dict(self):
        a = Alert(
            type="cpu",
            title="High CPU",
            description="CPU at 95%",
            severity="warning",
            action_label="Fix",
            action_payload={"cmd": "cleanup"},
        )
        d = a.to_dict()
        assert d["type"] == "cpu"
        assert d["title"] == "High CPU"
        assert d["severity"] == "warning"
        assert d["action_label"] == "Fix"
        assert d["action_payload"] == {"cmd": "cleanup"}

    def test_to_dict_roundtrip(self):
        a = Alert(type="memory", title="Memory", description="90% used", severity="warning")
        d = a.to_dict()
        assert d["type"] == "memory"
        assert d["description"] == "90% used"


class TestBaseMonitor:
    def test_raises_not_implemented(self):
        m = BaseMonitor(interval=1.0)
        with pytest.raises(NotImplementedError):
            asyncio.run(m.check())

    def test_interval_property(self):
        m = BaseMonitor(interval=5.0)
        assert m.interval == 5.0
        assert m._last_run == 0.0

    @pytest.mark.asyncio
    async def test_run_respects_interval(self):
        class FastMonitor(BaseMonitor):
            def __init__(self):
                super().__init__(interval=0.05)
                self.call_count = 0

            async def check(self):
                self.call_count += 1
                return None

            async def run(self, alert_queue):
                while True:
                    now = time.time()
                    if now - self._last_run >= self.interval:
                        self._last_run = now
                        try:
                            alert = await self.check()
                            if alert is not None:
                                await alert_queue.put(alert)
                        except Exception:
                            pass
                    await asyncio.sleep(0.01)

        m = FastMonitor()
        queue: asyncio.Queue = asyncio.Queue()
        task = asyncio.create_task(m.run(queue))
        await asyncio.sleep(0.2)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        assert m.call_count >= 2


class TestProactiveMonitor:
    @pytest.mark.asyncio
    async def test_add_and_start_stop(self):
        pm = ProactiveMonitor()
        assert len(pm._monitors) == 0
        assert not pm._running

        class DummyMonitor(BaseMonitor):
            def __init__(self):
                super().__init__(interval=999)

            async def check(self):
                return None

        m = DummyMonitor()
        pm.add_monitor(m)
        assert len(pm._monitors) == 1

        pm.start()
        assert pm._running is True
        assert len(pm._tasks) == 1

        pm.stop()
        assert pm._running is False
        assert len(pm._tasks) == 0

    def test_start_idempotent(self):
        pm = ProactiveMonitor()
        pm.start()
        pm.start()
        assert pm._running is True
        pm.stop()

    @pytest.mark.asyncio
    async def test_get_alerts(self):
        pm = ProactiveMonitor()
        alert = Alert(type="test", title="Test alert", description="Desc")
        pm._alert_queue.put_nowait(alert)
        alerts = await pm.get_alerts(max_count=10)
        assert len(alerts) == 1
        assert alerts[0].title == "Test alert"

    @pytest.mark.asyncio
    async def test_get_alert_count(self):
        pm = ProactiveMonitor()
        assert pm.get_alert_count() == 0
        pm._alert_queue.put_nowait(Alert(type="t", title="T", description="D"))
        assert pm.get_alert_count() == 1


@pytest.mark.asyncio
async def test_screen_monitor_no_pil():
    from core.proactive import ScreenMonitor

    m = ScreenMonitor(interval=999)
    result = await m.check()
    assert result is None


@pytest.mark.asyncio
async def test_system_monitor_no_psutil(monkeypatch):
    import core.proactive

    monkeypatch.setattr(core.proactive, "psutil", None)
    from core.proactive import SystemMonitor

    m = SystemMonitor(interval=999)
    result = await m.check()
    assert result is None

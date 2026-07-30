import time

import pytest

from core.automations import Automation, AutomationEngine, _cron_match


class TestAutomation:
    def test_to_dict_roundtrip(self):
        auto = Automation(
            id="test123", name="Test", trigger_type="cron",
            trigger_config={"cron": "0 8 * * *"}, action="notification",
            action_params={"message": "hello"}, run_count=0,
        )
        d = auto.to_dict()
        restored = Automation.from_dict(d)
        assert restored.id == "test123"
        assert restored.name == "Test"
        assert restored.trigger_config["cron"] == "0 8 * * *"

    def test_default_values(self):
        auto = Automation(
            id="a", name="A", trigger_type="event",
            trigger_config={}, action="briefing", action_params={},
        )
        assert auto.enabled is True
        assert auto.run_count == 0
        assert auto.last_run is None


class TestCronMatch:
    def test_wildcard(self):
        import time as t
        now = t.localtime()
        assert _cron_match("* * * * *", now)

    def test_specific_minute(self):
        now = time.strptime("2025-01-01 08:30", "%Y-%m-%d %H:%M")
        assert _cron_match("30 8 * * *", now)

    def test_no_match(self):
        now = time.strptime("2025-01-01 08:30", "%Y-%m-%d %H:%M")
        assert not _cron_match("0 9 * * *", now)

    def test_step(self):
        now = time.strptime("2025-01-01 08:15", "%Y-%m-%d %H:%M")
        assert _cron_match("*/15 * * * *", now)

    def test_range(self):
        now = time.strptime("2025-01-01 10:00", "%Y-%m-%d %H:%M")
        assert _cron_match("0 9-17 * * 1-5", now)

    def test_list(self):
        now = time.strptime("2025-01-01 08:30", "%Y-%m-%d %H:%M")
        assert _cron_match("30,45 8 * * *", now)

    def test_invalid_expr(self):
        now = time.localtime()
        assert not _cron_match("invalid", now)
        assert not _cron_match("", now)


class TestAutomationEngine:
    @pytest.fixture
    def engine(self, tmp_path):
        path = tmp_path / "test_automations.json"
        return AutomationEngine(str(path))

    def test_create(self, engine):
        auto = engine.create("Morning Briefing", "cron",
                             {"cron": "0 8 * * *"}, "briefing")
        assert auto.name == "Morning Briefing"
        assert auto.id is not None
        assert auto.enabled is True

    def test_get(self, engine):
        created = engine.create("Test", "cron", {"cron": "* * * * *"}, "notification")
        fetched = engine.get(created.id)
        assert fetched is not None
        assert fetched.id == created.id

    def test_get_missing(self, engine):
        assert engine.get("nonexistent") is None

    def test_list_all(self, engine):
        engine.create("A", "cron", {}, "notification")
        engine.create("B", "event", {}, "briefing")
        assert len(engine.list_all()) == 2

    def test_update(self, engine):
        auto = engine.create("Original", "cron", {}, "notification")
        engine.update(auto.id, name="Updated", action="briefing")
        fetched = engine.get(auto.id)
        assert fetched.name == "Updated"
        assert fetched.action == "briefing"

    def test_update_missing(self, engine):
        assert engine.update("nope", name="X") is None

    def test_delete(self, engine):
        auto = engine.create("ToDelete", "cron", {}, "notification")
        assert engine.delete(auto.id) is True
        assert engine.get(auto.id) is None

    def test_delete_missing(self, engine):
        assert engine.delete("nope") is False

    def test_toggle(self, engine):
        auto = engine.create("ToggleMe", "cron", {}, "notification")
        assert engine.get(auto.id).enabled is True
        engine.toggle(auto.id)
        assert engine.get(auto.id).enabled is False
        engine.toggle(auto.id)
        assert engine.get(auto.id).enabled is True

    def test_execute_notification(self, engine):
        auto = engine.create("Notif", "cron", {}, "notification",
                             {"message": "test msg"})
        result = engine.execute(auto)
        assert result["type"] == "notification"
        assert result["message"] == "test msg"

    def test_execute_briefing(self, engine):
        auto = engine.create("Brief", "cron", {}, "briefing")
        result = engine.execute(auto)
        assert result["type"] == "briefing"

    def test_execute_tool_call(self, engine):
        auto = engine.create("Tool", "cron", {}, "tool_call",
                             {"tool": "web_fetch", "args": {"url": "https://example.com"}})
        result = engine.execute(auto)
        assert result["type"] == "tool_call"
        assert result["tool"] == "web_fetch"

    def test_execute_unknown(self, engine):
        auto = engine.create("Bad", "cron", {}, "unknown_action")
        result = engine.execute(auto)
        assert result["type"] == "unknown"

    def test_record_run(self, engine):
        auto = engine.create("Run", "cron", {}, "notification")
        engine.record_run(auto.id, "success")
        fetched = engine.get(auto.id)
        assert fetched.last_status == "success"
        assert fetched.run_count == 1

    def test_persistence(self, tmp_path):
        path = tmp_path / "persist.json"
        engine1 = AutomationEngine(str(path))
        engine1.create("Persistent", "cron", {"cron": "0 9 * * *"}, "briefing")
        engine2 = AutomationEngine(str(path))
        assert len(engine2.list_all()) == 1
        assert engine2.list_all()[0].name == "Persistent"

    def test_check_triggers_cron(self, engine):
        import time as t
        now = t.localtime()
        cron_expr = f"{now.tm_min} {now.tm_hour} * * *"
        engine.create("NowTrigger", "cron", {"cron": cron_expr}, "notification")
        fired = engine.check_triggers()
        assert len(fired) > 0
        assert fired[0].name == "NowTrigger"

    def test_check_triggers_disabled(self, engine):
        auto = engine.create("Disabled", "cron", {"cron": "* * * * *"}, "notification")
        engine.update(auto.id, enabled=False)
        fired = engine.check_triggers()
        assert len(fired) == 0

    def test_check_triggers_threshold_skipped(self, engine):
        engine.create("Threshold", "threshold", {"metric": "cpu", "min": 90}, "notification")
        fired = engine.check_triggers()
        assert len(fired) == 0  # threshold is evaluated externally

    def test_should_fire_cron(self, engine):
        import time as t
        now = t.localtime()
        cron_expr = f"{now.tm_min} {now.tm_hour} * * *"
        auto = engine.create("FireCheck", "cron", {"cron": cron_expr}, "notification")
        last_check = {}
        result = engine.should_fire_cron(auto.id, last_check)
        assert result is True

    def test_should_fire_cron_deduplicates(self, engine):
        import time as t
        now = t.localtime()
        cron_expr = f"{now.tm_min} {now.tm_hour} * * *"
        auto = engine.create("Dedup", "cron", {"cron": cron_expr}, "notification")
        last_check = {auto.id: time.time()}
        result = engine.should_fire_cron(auto.id, last_check)
        assert result is False  # within 55s window

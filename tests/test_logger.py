import pytest
from core.logger import (
    info, warn, error, debug,
    record_tool_call, record_llm_call, record_retry,
    get_metrics, reset_metrics, Timer, get_timeline,
)


class TestLogger:
    def test_info(self):
        info("test info", phase="test")
        assert True

    def test_warn(self):
        warn("test warn")
        assert True

    def test_error(self):
        error("test error")
        assert True

    def test_debug(self):
        debug("test debug")
        assert True


class TestMetrics:
    def setup_method(self):
        reset_metrics()

    def test_record_tool_call(self):
        record_tool_call("test_tool", 100.0)
        metrics = get_metrics()
        assert metrics["tools"]["test_tool"] == 1

    def test_record_tool_error(self):
        record_tool_call("failing_tool", 50.0, success=False)
        metrics = get_metrics()
        assert metrics["tool_errors"]["failing_tool"] == 1
        assert metrics["failures"] == 1

    def test_record_llm_call(self):
        record_llm_call(tokens=150)
        metrics = get_metrics()
        assert metrics["llm_calls"] == 1
        assert metrics["tokens_used"] == 150

    def test_record_retry(self):
        record_retry()
        metrics = get_metrics()
        assert metrics["retries"] == 1

    def test_reset_metrics(self):
        record_tool_call("x", 10.0)
        reset_metrics()
        metrics = get_metrics()
        assert metrics["llm_calls"] == 0

    def test_uptime(self):
        metrics = get_metrics()
        assert metrics["uptime_seconds"] >= 0

    def test_get_timeline(self):
        info("timeline test")
        timeline = get_timeline(limit=5)
        assert len(timeline) <= 5

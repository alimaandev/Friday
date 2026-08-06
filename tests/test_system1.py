import time

import pytest

from core.system1 import System1, build_default_system1


class TestSystem1:
    @pytest.fixture
    def s1(self):
        return System1()

    def test_register_and_route(self, s1):
        s1.register("ping", r"\bping\b", lambda q: "pong")
        result = s1.route("say ping")
        assert result is not None
        assert result["content"] == "pong"
        assert result["reflex"] == "ping"
        assert result["type"] == "fast"

    def test_no_match_returns_none(self, s1):
        result = s1.route("something completely different")
        assert result is None

    def test_priority_ordering(self, s1):
        s1.register("second", r"\btest\b", lambda q: "second", priority=50)
        s1.register("first", r"\btest\b", lambda q: "first", priority=10)
        result = s1.route("this is a test")
        assert result["content"] == "first"

    def test_handler_returning_none_skips(self, s1):
        s1.register("skip", r"\bskip\b", lambda q: None)
        s1.register("catch", r"\bskip\b", lambda q: "caught", priority=200)
        result = s1.route("skip me")
        assert result["content"] == "caught"

    def test_cache(self, s1):
        call_count = 0

        def handler(q):
            nonlocal call_count
            call_count += 1
            return "cached_result"

        s1.register("cached", r"\bcache\b", handler, cache_ttl=60)
        result1 = s1.route("use cache")
        result2 = s1.route("use cache")
        assert result1["cached"] is False
        assert result2["cached"] is True
        assert call_count == 1
        assert result2["content"] == "cached_result"

    def test_cache_expiry(self, s1):
        call_count = 0

        def handler(q):
            nonlocal call_count
            call_count += 1
            return f"result_{call_count}"

        s1.register("expire", r"\bexpire\b", handler, cache_ttl=1)
        s1.route("expire test")
        s1.route("expire test")  # cached
        time.sleep(1.1)
        s1.route("expire test")  # should re-run
        assert call_count == 2

    def test_handler_exception_skips(self, s1):
        s1.register("fails", r"\bfail\b", lambda q: 1 / 0)
        result = s1.route("this will fail")
        assert result is None

    def test_stats(self, s1):
        s1.register("stat1", r"\bstat1\b", lambda q: "a")
        s1.register("stat2", r"\bstat2\b", lambda q: "b")
        stats = s1.stats()
        assert len(stats) >= 2
        labels = [s["label"] for s in stats]
        assert "stat1" in labels
        assert "stat2" in labels

    def test_count(self, s1):
        start = s1.count()
        s1.register("extra", r"\bextra\b", lambda q: "x")
        assert s1.count() == start + 1

    def test_hit_count_increments(self, s1):
        s1.register("hit", r"\bhit\b", lambda q: "hit")
        s1.route("hit me")
        s1.route("hit me")
        stats = s1.stats()
        hit_stats = [s for s in stats if s["label"] == "hit"][0]
        assert hit_stats["hit_count"] == 2


class TestDefaultSystem1:
    def test_build_default(self):
        s1 = build_default_system1()
        assert s1.count() >= 8  # time, date, weather, system_info, memory_recall, news, create_automation, vision

    def test_time_reflex(self):
        s1 = build_default_system1()
        result = s1.route("what time is it")
        assert result is not None
        assert result["reflex"] == "time"
        assert (
            "20" in result["content"]
            or "AM" in result["content"]
            or "PM" in result["content"]
            or ":" in result["content"]
        )

    def test_date_reflex(self):
        s1 = build_default_system1()
        result = s1.route("what is today's date")
        assert result is not None
        assert result["reflex"] == "date"

    def test_weather_reflex(self):
        s1 = build_default_system1()
        result = s1.route("what's the weather")
        # May return None if network is unavailable
        if result:
            assert result["reflex"] == "weather"

    def test_system_info_reflex(self):
        s1 = build_default_system1()
        result = s1.route("system status")
        if result:
            assert result["reflex"] == "system_info"

    def test_news_reflex(self):
        s1 = build_default_system1()
        result = s1.route("latest news")
        if result:
            assert result["reflex"] == "news"

    def test_create_automation_reflex(self):
        s1 = build_default_system1()
        result = s1.route("create an automation called Daily Briefing every morning at 8am")
        if result:
            assert result["reflex"] == "create_automation"
            assert "Automation created" in result["content"] or "Could not" in result["content"]

    def test_vision_reflex(self):
        s1 = build_default_system1()
        result = s1.route("what's on my screen")
        if result:
            assert result["reflex"] == "vision"

    def test_no_false_positive(self):
        s1 = build_default_system1()
        result = s1.route("hello how are you")
        assert result is None

import re
import time
from collections.abc import Callable
from dataclasses import dataclass

from core.logger import info


@dataclass
class Reflex:
    label: str
    pattern: re.Pattern
    handler: Callable[[str], str | None]
    priority: int = 100
    hit_count: int = 0
    cached_response: str | None = None
    cache_ttl: float = 0
    cache_time: float = 0


class System1:
    def __init__(self):
        self._reflexes: list[Reflex] = []
        self._compiled_from_history: list[Reflex] = []

    def register(
        self, label: str, pattern: str, handler: Callable[[str], str | None], priority: int = 100, cache_ttl: float = 0
    ):
        self._reflexes.append(
            Reflex(
                label=label,
                pattern=re.compile(pattern, re.I),
                handler=handler,
                priority=priority,
                cache_ttl=cache_ttl,
            )
        )
        self._reflexes.sort(key=lambda r: r.priority)

    def route(self, user_input: str) -> dict | None:
        for reflex in self._reflexes:
            m = reflex.pattern.search(user_input)
            if not m:
                continue
            reflex.hit_count += 1
            cached_valid = False
            if reflex.cached_response is not None and reflex.cache_ttl > 0:
                if time.time() - reflex.cache_time < reflex.cache_ttl:
                    cached_valid = True
            if cached_valid:
                return {
                    "type": "fast",
                    "content": reflex.cached_response,
                    "reflex": reflex.label,
                    "cached": True,
                }
            try:
                result = reflex.handler(user_input)
                if result is None:
                    continue
                if reflex.cache_ttl > 0:
                    reflex.cached_response = result
                    reflex.cache_time = time.time()
                return {
                    "type": "fast",
                    "content": result,
                    "reflex": reflex.label,
                    "cached": False,
                }
            except Exception as e:
                info(f"Reflex '{reflex.label}' error: {e}")
                continue
        return None

    def learn(self, user_input: str, plan_tool: str | None, duration: float):
        if not plan_tool or not user_input:
            return
        tool_words = set(plan_tool.lower().replace("_", " ").split())
        input_words = set(user_input.lower().split())
        common = tool_words & input_words
        if common:
            pattern_words = "|".join(re.escape(w) for w in common)
            pattern = rf"\b({pattern_words})\b"
            try:
                existing = {r.pattern.pattern for r in self._reflexes}
                if pattern not in existing:
                    self._compiled_from_history.append(
                        Reflex(
                            label=f"learned_{plan_tool}",
                            pattern=re.compile(pattern, re.I),
                            handler=lambda _, t=plan_tool: (
                                f"I notice you're asking about {t}. Try using the {plan_tool} tool for this."
                            ),
                            priority=200,
                        )
                    )
            except re.error:
                pass
        if len(self._compiled_from_history) > 50:
            self._compiled_from_history.sort(key=lambda r: r.hit_count)
            self._compiled_from_history = self._compiled_from_history[-30:]

    def count(self) -> int:
        return len(self._reflexes) + len(self._compiled_from_history)

    def stats(self) -> list[dict]:
        stats = []
        for r in self._reflexes:
            stats.append(
                {
                    "label": r.label,
                    "priority": r.priority,
                    "hit_count": r.hit_count,
                    "pattern": r.pattern.pattern,
                }
            )
        return stats


_date_formats = [
    "%A, %B %d, %Y",
    "%Y-%m-%d %H:%M",
    "%I:%M %p",
]


def _handle_time(query: str) -> str | None:
    now = time.localtime()
    return f"{time.strftime('%A, %B %d, %Y', now)}\n{time.strftime('%I:%M %p', now)}"


def _handle_date(query: str) -> str | None:
    now = time.localtime()
    return time.strftime("%A, %B %d, %Y", now)


def _handle_weather(query: str) -> str | None:
    try:
        import json
        import urllib.request

        url = (
            "https://api.open-meteo.com/v1/forecast?"
            "latitude=33.68&longitude=73.05"
            "&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "Friday/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        cur = data.get("current", {})
        temp = cur.get("temperature_2m", "?")
        feels = cur.get("apparent_temperature", "?")
        humidity = cur.get("relative_humidity_2m", "?")
        wind = cur.get("wind_speed_10m", "?")
        code = cur.get("weather_code", 0)
        _weather_labels = {
            0: "Clear",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Foggy",
            51: "Light drizzle",
            61: "Rain",
            71: "Snow",
            80: "Rain showers",
            95: "Thunderstorm",
        }
        label = _weather_labels.get(code, "Unknown")
        return f"{temp}°C, {label}. Feels like {feels}°C. Humidity: {humidity}%. Wind: {wind} km/h."
    except Exception:
        return None


def _handle_system_info(query: str) -> str | None:
    try:
        import os
        import platform

        import psutil

        cpu = psutil.cpu_percent(interval=0)
        mem = psutil.virtual_memory()
        return (
            f"Host: {platform.node()} | OS: {platform.system()} {platform.release()}\n"
            f"CPU: {os.cpu_count()} cores at {cpu}% | "
            f"RAM: {mem.used // (1024**3)}GB / {mem.total // (1024**3)}GB ({mem.percent}%)"
        )
    except Exception:
        return None


def _handle_memory_recall(query: str) -> str | None:
    try:
        from core.memory import get_memory_manager

        mm = get_memory_manager()
        search_term = re.sub(
            r"(?i)(remember|recall|what (do you know|did i)|search memory|find memory|look up)", "", query
        ).strip()
        if search_term:
            results = mm.search(search_term, top_k=3)
            if results:
                lines = ["Relevant memories:"]
                for r in results:
                    text = r.get("text", r.get("value", ""))
                    score = r.get("score", 0)
                    lines.append(f"  [{score:.2f}] {text[:160]}")
                return "\n".join(lines)
        return None
    except Exception:
        return None


def _handle_news(query: str) -> str | None:
    try:
        import urllib.request
        import xml.etree.ElementTree as ET

        feeds = [
            "https://hnrss.org/frontpage",
            "http://feeds.bbci.co.uk/news/rss.xml",
        ]
        items = []
        for url in feeds:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Friday/1.0"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    root = ET.fromstring(resp.read())
                    for entry in root.findall(".//item")[:3]:
                        title = entry.findtext("title", "")
                        if title:
                            items.append(title)
            except Exception:
                continue
        if items:
            return "Latest headlines:\n" + "\n".join(f"  \u2022 {t}" for t in items)
        return None
    except Exception:
        return None


def _handle_create_automation(query: str) -> str | None:
    """Parse natural-language automation creation requests."""
    try:
        from core.automations import get_automation_engine

        q = query.lower()

        # Extract name
        name_match = re.search(r"(?:called|named|to )([a-z0-9 _-]+?)(?: (every|each|when|if|at|on|that))", q)
        name = name_match.group(1).strip().title() if name_match else "Custom Automation"

        # Detect trigger type
        cron_match = re.search(
            r"(?:(every|each|everyday|daily|weekly|monthly|hourly)"
            r"|(at\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?)"
            r"|(\d+)\s*(minute|hour|day)s?\s*ly?)",
            q,
        )
        trigger_type = "cron"
        trigger_config = {"cron": "0 0 * * *"}  # default: daily midnight

        if cron_match:
            trigger_config = _parse_cron_from_text(q)

        # Detect action
        action = "notification"
        action_params = {"message": f"⏰ Automation triggered: {name}"}

        if re.search(r"\b(briefing|morning (report|briefing)|daily (summary|digest))\b", q):
            action = "briefing"
            action_params = {}
        elif re.search(r"\b(tool|run|execute|call)\b", q):
            action = "tool_call"
            tool_match = re.search(r"(?:use|run|call|execute) (\w+)", q)
            action_params = {
                "tool": tool_match.group(1) if tool_match else "default",
                "args": {},
            }

        engine = get_automation_engine()
        auto = engine.create(name, trigger_type, trigger_config, action, action_params)
        return (
            f'✅ Automation created: "{auto.name}"\n'
            f"   Trigger: {trigger_type} ({trigger_config.get('cron', '')})\n"
            f"   Action: {action}\n"
            f"   Use `/api/v1/automations/{auto.id}` to manage it."
        )
    except Exception as e:
        return f"Could not create automation: {e}"


def _parse_cron_from_text(text: str) -> dict:
    """Convert natural language to a cron expression."""
    text = text.lower()

    # Hourly: "every hour", "every 2 hours"
    m = re.search(r"every\s+(\d+)?\s*hour", text)
    if m:
        interval = int(m.group(1)) if m.group(1) else 1
        return {"cron": f"0 */{interval} * * *"}

    # Minutes: "every 15 minutes", "every 5 min"
    m = re.search(r"every\s+(\d+)\s*(minute|min)", text)
    if m:
        return {"cron": f"*/{m.group(1)} * * * *"}

    # Daily at specific time: "at 8am", "at 09:30", "every day at 7"
    m = re.search(r"(?:at\s+)(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text)
    if m:
        hour = int(m.group(1))
        minute = int(m.group(2)) if m.group(2) else 0
        period = m.group(3)
        if period == "pm" and hour < 12:
            hour += 12
        if period == "am" and hour == 12:
            hour = 0
        return {"cron": f"{minute} {hour} * * *"}

    # Weekly: "every monday", "on mondays"
    days = {"monday": 1, "tuesday": 2, "wednesday": 3, "thursday": 4, "friday": 5, "saturday": 6, "sunday": 0}
    for day_name, day_num in days.items():
        if day_name in text:
            m = re.search(r"(?:at\s+)(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text)
            if m:
                hour = int(m.group(1))
                minute = int(m.group(2)) if m.group(2) else 0
                period = m.group(3)
                if period == "pm" and hour < 12:
                    hour += 12
                if period == "am" and hour == 12:
                    hour = 0
                return {"cron": f"{minute} {hour} * * {day_num}"}
            return {"cron": f"0 9 * * {day_num}"}

    # Weekdays: "every weekday", "weekdays"
    if re.search(r"weekday|business day", text):
        m = re.search(r"(?:at\s+)(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text)
        if m:
            hour = int(m.group(1))
            minute = int(m.group(2)) if m.group(2) else 0
            period = m.group(3)
            if period == "pm" and hour < 12:
                hour += 12
            if period == "am" and hour == 12:
                hour = 0
            return {"cron": f"{minute} {hour} * * 1-5"}
        return {"cron": "0 9 * * 1-5"}

    # Daily: "every day", "daily"
    if re.search(r"(daily|every day|each day|every morning|every evening)", text):
        m = re.search(r"(?:at\s+)(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text)
        if m:
            hour = int(m.group(1))
            minute = int(m.group(2)) if m.group(2) else 0
            period = m.group(3)
            if period == "pm" and hour < 12:
                hour += 12
            if period == "am" and hour == 12:
                hour = 0
            return {"cron": f"{minute} {hour} * * *"}
        return {"cron": "0 8 * * *"}

    return {"cron": "0 8 * * *"}


def _handle_vision_query(query: str) -> str | None:
    """Handle 'what's on my screen' type queries."""
    try:
        from core.vision import get_vision_engine

        engine = get_vision_engine()
        result = engine.describe_screen()
        if "error" in result:
            return None
        desc = result.get("description", "")
        text = result.get("text")
        parts = [desc]
        if text:
            parts.append(f"\nText detected on screen:\n{text[:500]}")
        return "".join(parts)
    except Exception:
        return None


def build_default_system1() -> System1:
    s1 = System1()
    s1.register("time", r"\b(what|current|tell|show).*time\b", _handle_time, priority=10, cache_ttl=10)
    s1.register("date", r"\b(what|current|today'?s|tell|show).*date\b", _handle_date, priority=10, cache_ttl=30)
    s1.register(
        "weather",
        r"\b(weather|temperature|forecast|how.*(hot|cold|warm))\b",
        _handle_weather,
        priority=20,
        cache_ttl=300,
    )
    s1.register(
        "system_info",
        r"\b(system|(cpu|memory|ram|disk)\s*(usage|info|status)|how.*system|performance)\b",
        _handle_system_info,
        priority=50,
        cache_ttl=10,
    )
    s1.register(
        "memory_recall",
        r"\b(remember|recall|what (do you know|did i)|search memory|find memory|look up)\b",
        _handle_memory_recall,
        priority=60,
    )
    s1.register(
        "news", r"\b(news|headlines|what'?s (new|happening)|latest)\b", _handle_news, priority=70, cache_ttl=300
    )
    s1.register(
        "create_automation",
        r"\b(create|make|add|schedule|set up)\s+(automation|automatic|schedule|recurring|cron|routine|task)\b",
        _handle_create_automation,
        priority=30,
    )
    s1.register(
        "vision",
        r"\b(what.*(screen|display|monitor|desktop|window)|describe.*(screen|display)|read.*screen|screen.*(show|say|display)|look at screen)\b",
        _handle_vision_query,
        priority=40,
    )
    return s1

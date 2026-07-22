import re
import time
from dataclasses import dataclass, field
from typing import Any, Callable

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

    def register(self, label: str, pattern: str, handler: Callable[[str], str | None],
                 priority: int = 100, cache_ttl: float = 0):
        self._reflexes.append(Reflex(
            label=label,
            pattern=re.compile(pattern, re.I),
            handler=handler,
            priority=priority,
            cache_ttl=cache_ttl,
        ))
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
                    self._compiled_from_history.append(Reflex(
                        label=f"learned_{plan_tool}",
                        pattern=re.compile(pattern, re.I),
                        handler=lambda _, t=plan_tool: f"I notice you're asking about {t}. Try using the {plan_tool} tool for this.",
                        priority=200,
                    ))
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
            stats.append({
                "label": r.label,
                "priority": r.priority,
                "hit_count": r.hit_count,
                "pattern": r.pattern.pattern,
            })
        return stats


_date_formats = [
    "%A, %B %d, %Y",
    "%Y-%m-%d %H:%M",
    "%I:%M %p",
]


def _handle_time(query: str) -> str | None:
    now = time.localtime()
    return (
        f"{time.strftime('%A, %B %d, %Y', now)}\n"
        f"{time.strftime('%I:%M %p', now)}"
    )


def _handle_date(query: str) -> str | None:
    now = time.localtime()
    return time.strftime('%A, %B %d, %Y', now)


def _handle_weather(query: str) -> str | None:
    try:
        import urllib.request, json
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
        _weather_labels = {0: "Clear", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                           45: "Foggy", 48: "Foggy", 51: "Light drizzle", 61: "Rain",
                           71: "Snow", 80: "Rain showers", 95: "Thunderstorm"}
        label = _weather_labels.get(code, "Unknown")
        return f"{temp}°C, {label}. Feels like {feels}°C. Humidity: {humidity}%. Wind: {wind} km/h."
    except Exception:
        return None


def _handle_system_info(query: str) -> str | None:
    try:
        import platform, os, psutil
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
        search_term = re.sub(r"(?i)(remember|recall|what (do you know|did i)|search memory|find memory|look up)", "", query).strip()
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
        import urllib.request, xml.etree.ElementTree as ET
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


def build_default_system1() -> System1:
    s1 = System1()
    s1.register("time", r"\b(what|current|tell|show).*time\b", _handle_time, priority=10, cache_ttl=10)
    s1.register("date", r"\b(what|current|today'?s|tell|show).*date\b", _handle_date, priority=10, cache_ttl=30)
    s1.register("weather", r"\b(weather|temperature|forecast|how.*(hot|cold|warm))\b", _handle_weather, priority=20, cache_ttl=300)
    s1.register("system_info", r"\b(system|(cpu|memory|ram|disk)\s*(usage|info|status)|how.*system|performance)\b", _handle_system_info, priority=50, cache_ttl=10)
    s1.register("memory_recall", r"\b(remember|recall|what (do you know|did i)|search memory|find memory|look up)\b", _handle_memory_recall, priority=60)
    s1.register("news", r"\b(news|headlines|what'?s (new|happening)|latest)\b", _handle_news, priority=70, cache_ttl=300)
    return s1

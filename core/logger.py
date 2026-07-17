import json
import os
import time
import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

_LOG_FILE = os.path.join(LOG_DIR, "friday.log")
_EVENT_LOG = os.path.join(LOG_DIR, "events.jsonl")
_METRICS_LOG = os.path.join(LOG_DIR, "metrics.jsonl")

_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

_logger = logging.getLogger("friday")
_logger.setLevel(logging.DEBUG)
_logger.addHandler(_handler)

_METRICS: dict[str, Any] = {
    "tools": defaultdict(int),
    "tool_errors": defaultdict(int),
    "tool_durations": defaultdict(list),
    "tokens_used": 0,
    "llm_calls": 0,
    "failures": 0,
    "retries": 0,
    "started_at": time.time(),
}


def _event_log(entry: dict[str, Any]):
    try:
        with open(_EVENT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
    except Exception:
        pass


def _metrics_log(entry: dict[str, Any]):
    try:
        with open(_METRICS_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
    except Exception:
        pass


def log(level: str, message: str, **extra):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level.upper(),
        "message": message,
        **extra,
    }
    _logger.log(getattr(logging, level.upper(), logging.INFO), message)
    _event_log(entry)


def info(message: str, **extra):
    log("info", message, **extra)


def warn(message: str, **extra):
    log("warning", message, **extra)


def error(message: str, **extra):
    log("error", message, **extra)


def debug(message: str, **extra):
    log("debug", message, **extra)


class Timer:
    def __init__(self, label: str):
        self.label = label
        self.start: float | None = None

    def __enter__(self):
        self.start = time.monotonic()
        return self

    def __exit__(self, *args):
        elapsed = time.monotonic() - self.start
        info(f"{self.label} completed", duration_ms=round(elapsed * 1000, 1))


def record_tool_call(name: str, duration_ms: float, success: bool = True):
    _METRICS["tools"][name] += 1
    _METRICS["tool_durations"][name].append(duration_ms)
    if not success:
        _METRICS["tool_errors"][name] += 1
        _METRICS["failures"] += 1
    _metrics_log({
        "type": "tool_call",
        "tool": name,
        "duration_ms": round(duration_ms, 1),
        "success": success,
    })


def record_llm_call(tokens: int = 0):
    _METRICS["llm_calls"] += 1
    _METRICS["tokens_used"] += tokens


def record_retry():
    _METRICS["retries"] += 1


def get_metrics() -> dict:
    uptime = time.time() - _METRICS["started_at"]
    result = {
        "uptime_seconds": round(uptime, 1),
        "llm_calls": _METRICS["llm_calls"],
        "tokens_used": _METRICS["tokens_used"],
        "failures": _METRICS["failures"],
        "retries": _METRICS["retries"],
        "tools": dict(_METRICS["tools"]),
        "tool_errors": dict(_METRICS["tool_errors"]),
    }
    avg_durations = {}
    for name, durations in _METRICS["tool_durations"].items():
        if durations:
            avg_durations[name] = round(sum(durations) / len(durations), 1)
    result["avg_tool_duration_ms"] = avg_durations
    return result


def reset_metrics():
    _METRICS.clear()
    _METRICS.update({
        "tools": defaultdict(int),
        "tool_errors": defaultdict(int),
        "tool_durations": defaultdict(list),
        "tokens_used": 0,
        "llm_calls": 0,
        "failures": 0,
        "retries": 0,
        "started_at": time.time(),
    })


def get_timeline(limit: int = 50) -> list[dict]:
    events = []
    if os.path.exists(_EVENT_LOG):
        try:
            with open(_EVENT_LOG, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        events.append(json.loads(line))
        except Exception:
            pass
    return events[-limit:]

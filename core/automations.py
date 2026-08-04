"""Automation engine for Friday — cron, threshold, and event triggers."""

import json
import os
import time
import uuid
from dataclasses import asdict, dataclass

AUTOMATIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "memory_store")
AUTOMATIONS_FILE = os.path.join(AUTOMATIONS_DIR, "automations.json")


@dataclass
class Automation:
    id: str
    name: str
    trigger_type: str  # "cron", "threshold", "event"
    trigger_config: dict
    action: str  # "notification", "briefing", "tool_call"
    action_params: dict
    enabled: bool = True
    created_at: float = 0
    last_run: float | None = None
    last_status: str | None = None  # "success", "error"
    run_count: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Automation":
        return cls(**data)


def _cron_match(cron_expr: str, t: time.struct_time) -> bool:
    """Match a 5-field cron expression against a time struct."""
    fields = cron_expr.strip().split()
    if len(fields) != 5:
        return False
    minute, hour, dom, month, dow = fields
    return (
        _cron_field_match(minute, t.tm_min, 0, 59)
        and _cron_field_match(hour, t.tm_hour, 0, 23)
        and _cron_field_match(dom, t.tm_mday, 1, 31)
        and _cron_field_match(month, t.tm_mon, 1, 12)
        and _cron_field_match(dow, t.tm_wday, 0, 6)
    )


def _cron_field_match(pattern: str, value: int, lo: int, hi: int) -> bool:
    """Match a single cron field value against a pattern."""
    if pattern == "*":
        return True
    for part in pattern.split(","):
        part = part.strip()
        if not part:
            continue
        if "/" in part:
            base, step = part.split("/", 1)
            step = int(step)
            if base == "*":
                base_low, base_high = lo, hi
            elif "-" in base:
                base_low, base_high = (int(x) for x in base.split("-", 1))
            else:
                base_low = base_high = int(base)
            if base_low <= value <= base_high and (value - base_low) % step == 0:
                return True
        elif "-" in part:
            a, b = (int(x) for x in part.split("-", 1))
            if a <= value <= b:
                return True
        elif part == "*":
            return True
        else:
            if int(part) == value:
                return True
    return False


class AutomationEngine:
    def __init__(self, file_path: str | None = None):
        self._file_path = file_path or AUTOMATIONS_FILE
        self._items: dict[str, Automation] = {}
        self._dirty = False
        os.makedirs(os.path.dirname(self._file_path), exist_ok=True)
        self._load()

    # ─── CRUD ─────────────────────────────────────────────────────

    def create(
        self, name: str, trigger_type: str, trigger_config: dict, action: str, action_params: dict | None = None
    ) -> Automation:
        auto = Automation(
            id=uuid.uuid4().hex[:12],
            name=name,
            trigger_type=trigger_type,
            trigger_config=trigger_config,
            action=action,
            action_params=action_params or {},
            created_at=time.time(),
        )
        self._items[auto.id] = auto
        self._dirty = True
        self._save()
        return auto

    def get(self, auto_id: str) -> Automation | None:
        return self._items.get(auto_id)

    def list_all(self) -> list[Automation]:
        return list(self._items.values())

    def update(self, auto_id: str, **kwargs) -> Automation | None:
        auto = self._items.get(auto_id)
        if not auto:
            return None
        for k, v in kwargs.items():
            if hasattr(auto, k):
                setattr(auto, k, v)
        self._dirty = True
        self._save()
        return auto

    def delete(self, auto_id: str) -> bool:
        if auto_id in self._items:
            del self._items[auto_id]
            self._dirty = True
            self._save()
            return True
        return False

    def toggle(self, auto_id: str) -> Automation | None:
        return self.update(auto_id, enabled=not self._items[auto_id].enabled)

    # ─── Trigger checking ─────────────────────────────────────────

    def check_triggers(self) -> list[Automation]:
        """Return all automations whose trigger conditions are met right now."""
        now = time.localtime()
        fired: list[Automation] = []
        for auto in self._items.values():
            if not auto.enabled:
                continue
            if auto.trigger_type == "cron":
                cron_expr = auto.trigger_config.get("cron", "")
                if cron_expr and _cron_match(cron_expr, now):
                    fired.append(auto)
            elif auto.trigger_type == "threshold":
                # evaluated externally via check_and_fire
                pass
            elif auto.trigger_type == "event":
                # evaluated externally via check_and_fire
                pass
        return fired

    def should_fire_cron(self, auto_id: str, last_check_key: dict[str, float]) -> bool:
        """Check if a cron automation should fire (deduplicated)."""
        auto = self._items.get(auto_id)
        if not auto or not auto.enabled or auto.trigger_type != "cron":
            return False
        now = time.localtime()
        if not _cron_match(auto.trigger_config.get("cron", ""), now):
            return False
        last = last_check_key.get(auto_id, 0)
        if time.time() - last < 55:
            return False
        # Avoid re-firing if we already ran this exact minute
        last_struct = time.localtime(last) if last else None
        if last_struct and (last_struct.tm_min == now.tm_min and last_struct.tm_hour == now.tm_hour):
            return False
        return True

    # ─── Action execution ─────────────────────────────────────────

    def execute(self, auto: Automation) -> dict:
        """Execute an automation's action. Returns result dict."""
        try:
            if auto.action == "notification":
                return {"type": "notification", "title": auto.name, "message": auto.action_params.get("message", "")}
            elif auto.action == "briefing":
                return {"type": "briefing", "source": "automation"}
            elif auto.action == "tool_call":
                return {
                    "type": "tool_call",
                    "tool": auto.action_params.get("tool", ""),
                    "args": auto.action_params.get("args", {}),
                }
            return {"type": "unknown", "error": f"Unknown action: {auto.action}"}
        except Exception as e:
            return {"type": "error", "error": str(e)}

    def record_run(self, auto_id: str, status: str):
        """Record an automation execution result."""
        auto = self._items.get(auto_id)
        if not auto:
            return
        auto.last_run = time.time()
        auto.last_status = status
        auto.run_count += 1
        self._dirty = True
        self._save()

    # ─── Persistence ──────────────────────────────────────────────

    def _load(self):
        try:
            with open(self._file_path, encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                auto = Automation.from_dict(item)
                self._items[auto.id] = auto
        except (FileNotFoundError, json.JSONDecodeError):
            self._items = {}

    def _save(self):
        data = [a.to_dict() for a in self._items.values()]
        try:
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass


_engine: AutomationEngine | None = None


def get_automation_engine() -> AutomationEngine:
    global _engine
    if _engine is None:
        _engine = AutomationEngine()
    return _engine


# ─── Cron expression examples ──────────────────────────────────
# "0 8 * * *"    → every day at 8:00 AM
# "*/15 * * * *" → every 15 minutes
# "0 9-17 * * 1-5" → weekdays 9 AM to 5 PM on the hour
# "30 7 * * 1"   → every Monday at 7:30 AM

import asyncio
import hashlib
import io
import time
from dataclasses import dataclass, field
from typing import Any, Callable

try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None

try:
    import psutil
except ImportError:
    psutil = None


@dataclass
class Alert:
    type: str
    title: str
    description: str
    severity: str = "info"
    action_label: str | None = None
    action_payload: dict | None = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "action_label": self.action_label,
            "action_payload": self.action_payload,
            "timestamp": self.timestamp,
        }


class BaseMonitor:
    def __init__(self, interval: float):
        self.interval = interval
        self._last_run = 0.0

    async def check(self) -> Alert | None:
        raise NotImplementedError

    async def run(self, alert_queue: asyncio.Queue):
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
            await asyncio.sleep(1)


class ScreenMonitor(BaseMonitor):
    def __init__(self, interval: float = 3.0):
        super().__init__(interval)
        self._prev_hash: int | None = None
        self._prev_meta: dict = {}
        self._region_hashes: list[list[str | None]] | None = None

    async def check(self) -> Alert | None:
        if ImageGrab is None:
            return None
        try:
            img = await asyncio.to_thread(ImageGrab.grab)
            buf = io.BytesIO()
            await asyncio.to_thread(lambda: img.save(buf, format="PNG"))
            h = hashlib.md5(buf.getvalue()).hexdigest()
            if self._prev_hash is not None and h != self._prev_hash:
                change = self._detect_region_change(img)
                self._prev_hash = h
                if change:
                    return Alert(
                        type="screen_change",
                        title="Screen changed",
                        description=f"New window or significant change detected in {change} region",
                        severity="info",
                    )
            if self._prev_hash is None:
                self._prev_hash = h
            self._prev_meta = {"width": img.width, "height": img.height}
        except Exception:
            pass
        return None

    def _detect_region_change(self, img) -> str | None:
        GRID_COLS, GRID_ROWS = 4, 3
        w, h = img.size
        cell_w, cell_h = w // GRID_COLS, h // GRID_ROWS
        if not hasattr(self, '_region_hashes') or self._region_hashes is None:
            self._region_hashes = [[None] * GRID_COLS for _ in range(GRID_ROWS)]
        changed: list[str] = []
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                left = col * cell_w
                top = row * cell_h
                right = left + cell_w if col < GRID_COLS - 1 else w
                bottom = top + cell_h if row < GRID_ROWS - 1 else h
                region = img.crop((left, top, right, bottom))
                h_val = hashlib.md5(region.tobytes()).hexdigest()
                prev = self._region_hashes[row][col]
                if prev is not None and h_val != prev:
                    region_names = ["top-left", "top-center", "top-right", "top-rightmost",
                                    "mid-left", "mid-center", "mid-right", "mid-rightmost",
                                    "bottom-left", "bottom-center", "bottom-right", "bottom-rightmost"]
                    idx = row * GRID_COLS + col
                    changed.append(region_names[idx] if idx < len(region_names) else f"region-{idx}")
                self._region_hashes[row][col] = h_val
        if len(changed) >= 3:
            return "large area"
        if len(changed) == 2:
            return f"{changed[0]} and {changed[1]}"
        if len(changed) == 1:
            return changed[0]
        return None


class CalendarMonitor(BaseMonitor):
    def __init__(self, interval: float = 60.0):
        super().__init__(interval)
        self._known_events: set[str] = set()

    async def check(self) -> Alert | None:
        try:
            from core.auth.google import get_calendar_service, is_authenticated
            if not is_authenticated():
                return None
            from datetime import datetime, timezone, timedelta
            service = get_calendar_service()
            now = datetime.now(timezone.utc)
            soon = (now + timedelta(hours=2)).isoformat()
            events = service.events().list(
                calendarId="primary",
                timeMin=now.isoformat(),
                timeMax=soon,
                maxResults=5,
                singleEvents=True,
                orderBy="startTime",
            ).execute()

            alerts = []
            for e in events.get("items", []):
                eid = e.get("id", "")
                if eid in self._known_events:
                    continue
                self._known_events.add(eid)
                start_str = e["start"].get("dateTime", e["start"].get("date", ""))
                summary = e.get("summary", "Untitled event")
                if start_str:
                    try:
                        start_dt = datetime.fromisoformat(start_str)
                        mins_until = (start_dt - now).total_seconds() / 60
                        if 0 <= mins_until <= 15:
                            desc = f'"{summary}" starts in {int(mins_until)} minutes'
                            if e.get("location"):
                                desc += f" at {e['location']}"
                            return Alert(
                                type="meeting_reminder",
                                title="Upcoming meeting",
                                description=desc,
                                severity="info",
                            )
                    except Exception:
                        pass

            if len(self._known_events) > 100:
                self._known_events = set(list(self._known_events)[-50:])
        except Exception:
            pass
        return None


class EmailMonitor(BaseMonitor):
    def __init__(self, interval: float = 120.0):
        super().__init__(interval)
        self._known_ids: set[str] = set()
        self._last_unread = 0

    async def check(self) -> Alert | None:
        try:
            from core.auth.google import get_gmail_service, is_authenticated
            if not is_authenticated():
                return None
            service = get_gmail_service()
            results = service.users().messages().list(
                userId="me", maxResults=5, q="is:unread"
            ).execute()
            msgs = results.get("messages", [])
            current_ids = {m["id"] for m in msgs}
            new_ids = current_ids - self._known_ids
            self._known_ids |= current_ids
            if len(self._known_ids) > 200:
                self._known_ids = set(list(self._known_ids)[-100:])

            urgencies = {"urgent", "important", "asap", "deadline", "action required"}
            for mid in list(new_ids)[:3]:
                try:
                    meta = service.users().messages().get(
                        userId="me", id=mid, format="metadata",
                        metadataHeaders=["From", "Subject"],
                    ).execute()
                    headers = {h["name"]: h["value"] for h in meta.get("payload", {}).get("headers", [])}
                    subj = headers.get("Subject", "").lower()
                    frm = headers.get("From", "")
                    snippet = meta.get("snippet", "")
                    for keyword in urgencies:
                        if keyword in subj:
                            return Alert(
                                type="email_urgent",
                                title="Urgent email",
                                description=f'From: {frm}\nSubject: {headers.get("Subject", "")}',
                                severity="warning",
                                action_label="Open inbox",
                                action_payload={"source": "email"},
                            )
                except Exception:
                    pass

            unread = results.get("resultSizeEstimate", 0)
            prev = self._last_unread
            self._last_unread = unread
            if prev > 0 and unread > prev + 3:
                return Alert(
                    type="email_influx",
                    title=f"{unread - prev} new emails",
                    description=f"Inbox now has {unread} unread messages",
                    severity="info",
                )
        except Exception:
            pass
        return None


class SystemMonitor(BaseMonitor):
    def __init__(self, interval: float = 30.0):
        super().__init__(interval)

    async def check(self) -> Alert | None:
        if psutil is None:
            return None
        try:
            cpu = await asyncio.to_thread(lambda: psutil.cpu_percent(interval=0.1))
            mem = await asyncio.to_thread(psutil.virtual_memory)
            disk = await asyncio.to_thread(lambda: psutil.disk_usage("/"))

            if cpu > 90:
                return Alert(
                    type="system_high_cpu",
                    title="High CPU usage",
                    description=f"CPU at {cpu}% — consider closing unused applications",
                    severity="warning",
                )
            if mem.percent > 85:
                return Alert(
                    type="system_high_memory",
                    title="High memory usage",
                    description=f"RAM at {mem.percent}% ({mem.used // (1024**3)}GB / {mem.total // (1024**3)}GB)",
                    severity="warning",
                )
            if disk.percent > 90:
                return Alert(
                    type="system_low_disk",
                    title="Low disk space",
                    description=f"Disk at {disk.percent}% ({disk.free // (1024**3)}GB free)",
                    severity="warning",
                )
        except Exception:
            pass
        return None


class ProactiveMonitor:
    def __init__(self):
        self._alert_queue: asyncio.Queue = asyncio.Queue()
        self._monitors: list[BaseMonitor] = []
        self._tasks: list[asyncio.Task] = []
        self._running = False

    def add_monitor(self, monitor: BaseMonitor):
        self._monitors.append(monitor)

    def start(self):
        if self._running:
            return
        self._running = True
        for monitor in self._monitors:
            task = asyncio.create_task(monitor.run(self._alert_queue))
            self._tasks.append(task)

    def stop(self):
        self._running = False
        for task in self._tasks:
            task.cancel()
        self._tasks.clear()

    async def get_alerts(self, max_count: int = 10) -> list[Alert]:
        alerts = []
        while not self._alert_queue.empty() and len(alerts) < max_count:
            try:
                alert = self._alert_queue.get_nowait()
                alerts.append(alert)
            except asyncio.QueueEmpty:
                break
        return alerts

    def get_alert_count(self) -> int:
        return self._alert_queue.qsize()

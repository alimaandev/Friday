"""Friday's Diary — narrative memory in plain markdown.

One markdown file per day (``logs/diary/YYYY-MM-DD.md``), written in Friday's
voice. Three sources feed it:

- ``record()`` — explicit entries (conversations, autopilot runs, alerts)
- ``write_day_entry()`` — nightly digest from long-term memory
- ``morning_note()`` — yesterday's highlights, fed into the daily briefing

Everything is deterministic and offline — no LLM calls required.
"""

import os
from datetime import UTC, date, datetime, timedelta

DIARY_DIR = os.getenv("FRIDAY_DIARY_DIR") or os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "diary"
)


class DiaryEngine:
    def __init__(self, diary_dir: str | None = None, memory_manager=None):
        self.diary_dir = diary_dir or DIARY_DIR
        os.makedirs(self.diary_dir, exist_ok=True)
        self._memory = memory_manager

    # ─── Paths & IO ────────────────────────────────────────────────

    def _path(self, day: date | None = None) -> str:
        return os.path.join(self.diary_dir, f"{(day or date.today()).isoformat()}.md")

    def record(self, title: str, body: str, kind: str = "entry", day: date | None = None) -> str:
        """Append a dated entry and return the page path."""
        path = self._path(day)
        stamp = datetime.now(UTC).strftime("%H:%M")
        block = [f"## {stamp} — {kind}", "", title, "", str(body), ""]
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n".join(block))
        return path

    def read(self, day: date | None = None) -> str:
        path = self._path(day)
        if not os.path.exists(path):
            return ""
        with open(path, encoding="utf-8") as f:
            return f.read()

    def recent(self, n: int = 7) -> list[dict]:
        """Latest entries across the last ``n`` pages (oldest of the batch first)."""
        files = [f for f in sorted(os.listdir(self.diary_dir)) if f.endswith(".md")][-n:]
        out: list[dict] = []
        for fn in files:
            try:
                with open(os.path.join(self.diary_dir, fn), encoding="utf-8") as f:
                    text = f.read()
            except OSError:
                continue
            excerpt = ""
            for line in text.splitlines():
                if line.strip() and not line.startswith("#"):
                    excerpt = line.strip()
                    break
            out.append({"date": fn[:-3], "excerpt": excerpt[:160]})
        return out

    # ─── Content generation ────────────────────────────────────────

    def digest_day(self, day: date | None = None) -> str:
        """Deterministic nightly digest: what Friday learned and remembers."""
        mm = self._memory or self._get_memory_manager()
        entries = [e for e in mm.list_all().get("entries", []) if str(e.get("value", "")).strip()]
        notable = sorted(entries, key=lambda e: e.get("importance", 0.5), reverse=True)[:3]
        fact_lines = [f"- {str(e.get('value', ''))[:160]}" for e in notable]

        parts = [f"Today I carry {len(entries)} facts in long-term memory."]
        if fact_lines:
            parts.append("The day's most important fragments:")
            parts.append("\n".join(fact_lines))
        else:
            parts.append("No new long-term memories were recorded today.")
        return "\n".join(parts)

    def write_day_entry(self, day: date | None = None) -> str:
        """Record tonight's digest as the day's closing entry."""
        body = self.digest_day(day)
        return self.record(
            title=f"Closing entry for {day or date.today()}",
            body=body,
            kind="Nightly digest",
            day=day,
        )

    def morning_note(self) -> str:
        """Yesterday's diary excerpt for the morning briefing (or '')."""
        path = self._path(date.today() - timedelta(days=1))
        if not os.path.exists(path):
            return ""
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except OSError:
            return ""
        excerpt = "".join(
            f"{line.strip()}\n" for line in text.splitlines() if line.strip() and not line.startswith("#")
        )
        return excerpt.strip()[:300]

    # ─── Helpers ───────────────────────────────────────────────────

    @staticmethod
    def _get_memory_manager():
        from core.memory import get_memory_manager

        return get_memory_manager()


def get_diary() -> DiaryEngine:
    global _diary
    if _diary is None:
        _diary = DiaryEngine()
    return _diary


_diary: DiaryEngine | None = None

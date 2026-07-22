import json
import os
import time
from typing import Any

from core.logger import info


class MemoryEntry:
    def __init__(self, key: str, value: Any, importance: float = 0.5):
        self.key = key
        self.value = value
        self.importance = importance
        self.created_at = time.time()
        self.accessed_at = time.time()
        self.access_count = 1
        self.summary: str | None = None

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "value": self.value,
            "importance": self.importance,
            "created_at": self.created_at,
            "accessed_at": self.accessed_at,
            "access_count": self.access_count,
            "summary": self.summary,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryEntry":
        entry = cls(data["key"], data["value"], data.get("importance", 0.5))
        entry.created_at = data.get("created_at", time.time())
        entry.accessed_at = data.get("accessed_at", time.time())
        entry.access_count = data.get("access_count", 1)
        entry.summary = data.get("summary")
        return entry

    def score(self) -> float:
        age = time.time() - self.created_at
        hours = age / 3600
        recency = 1.0 / (1.0 + hours / 24.0)
        frequency = 1.0 - 1.0 / (1.0 + self.access_count)
        return 0.4 * self.importance + 0.3 * recency + 0.3 * frequency


class LongTermMemory:
    def __init__(self, file_path: str, max_entries: int = 500):
        self._file_path = file_path
        self._max_entries = max_entries
        self._entries: dict[str, MemoryEntry] = {}
        self._dirty = False
        self._load()

    def store(self, key: str, value: Any, importance: float = 0.5) -> dict:
        if key in self._entries:
            entry = self._entries[key]
            entry.value = value
            entry.importance = max(entry.importance, importance)
            entry.accessed_at = time.time()
            entry.access_count += 1
        else:
            self._entries[key] = MemoryEntry(key, value, importance)
            if len(self._entries) > self._max_entries:
                self._evict()

        self._dirty = True
        return {"success": True, "key": key, "importance": importance}

    def recall(self, key: str) -> dict:
        entry = self._entries.get(key)
        if not entry:
            return {"key": key, "value": None, "error": f"No memory found for key '{key}'"}
        entry.accessed_at = time.time()
        entry.access_count += 1
        self._dirty = True
        return {"key": key, "value": entry.value, "source": "long_term"}

    def forget(self, key: str) -> dict:
        if key in self._entries:
            del self._entries[key]
            self._dirty = True
            return {"success": True, "key": key}
        return {"success": False, "key": key, "error": f"No memory found for key '{key}'"}

    def list_all(self) -> dict:
        entries = []
        for key, entry in self._entries.items():
            entries.append({
                "key": key,
                "importance": entry.importance,
                "score": round(entry.score(), 3),
                "access_count": entry.access_count,
                "summary": entry.summary or str(entry.value)[:80],
            })
        entries.sort(key=lambda e: e["score"], reverse=True)
        return {"entries": entries, "count": len(entries)}

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        query_lower = query.lower()
        scored = []
        for key, entry in self._entries.items():
            value_str = str(entry.value).lower()
            summary_str = (entry.summary or "").lower()
            if query_lower in key.lower() or query_lower in value_str or query_lower in summary_str:
                scored.append((entry.score(), key, entry.value))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [{"key": k, "value": v, "score": round(s, 3)} for s, k, v in scored[:top_k]]
        return results

    def persist(self):
        if not self._dirty:
            return
        self._dirty = False
        self._save()

    def decay(self, factor: float = 0.95):
        now = time.time()
        changed = False
        for entry in list(self._entries.values()):
            if now - entry.accessed_at > 86400 * 30:
                entry.importance *= factor
                if entry.importance < 0.1:
                    del self._entries[entry.key]
                    changed = True
        if changed:
            self._dirty = True

    def _evict(self):
        scored = [(entry.score(), key) for key, entry in self._entries.items()]
        scored.sort()
        to_remove = scored[:max(1, len(self._entries) - self._max_entries)]
        for _, key in to_remove:
            del self._entries[key]
        info(f"Evicted {len(to_remove)} low-importance memories")

    def _load(self):
        if not os.path.exists(self._file_path):
            return
        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                entry = MemoryEntry.from_dict(item)
                self._entries[entry.key] = entry
        except Exception as e:
            info(f"Failed to load long-term memory: {e}")

    def _save(self):
        try:
            data = [entry.to_dict() for entry in self._entries.values()]
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            info(f"Failed to save long-term memory: {e}")

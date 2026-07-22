import os
import pickle
import re
import time
from collections import Counter
from typing import Any

from core.logger import info

MEMORY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "memory_store")
VECTOR_STORE_PATH = os.path.join(MEMORY_DIR, "vector_store.pkl")
os.makedirs(MEMORY_DIR, exist_ok=True)

_WORD_RE = re.compile(r"\w+")


def _tokenize(text: str) -> set[str]:
    return set(w.lower() for w in _WORD_RE.findall(text))


def _token_freq(text: str) -> Counter:
    return Counter(w.lower() for w in _WORD_RE.findall(text))


def _jaccard_similarity(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _cosine_similarity(a: Counter, b: Counter) -> float:
    if not a or not b:
        return 0.0
    intersection = set(a) & set(b)
    numerator = sum(a[x] * b[x] for x in intersection)
    denom = (sum(v ** 2 for v in a.values()) ** 0.5) * (sum(v ** 2 for v in b.values()) ** 0.5)
    if not denom:
        return 0.0
    return numerator / denom


class VectorEntry:
    def __init__(self, text: str, metadata: dict | None = None):
        self.text = text
        self.tokens = _tokenize(text)
        self.freq = _token_freq(text)
        self.metadata = metadata or {}
        self.created_at = time.time()
        self.id = self.metadata.get("id", str(time.time()))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "text": self.text[:200],
            "metadata": self.metadata,
            "created_at": self.created_at,
        }


class VectorMemory:
    def __init__(self):
        self._entries: list[VectorEntry] = []
        self._dirty = False
        self._load()

    def store(self, text: str, metadata: dict | None = None) -> dict:
        entry = VectorEntry(text, metadata)
        self._entries.append(entry)
        self._dirty = True
        return {"id": entry.id, "text": text[:80], "success": True}

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        if not self._entries:
            return []
        qtokens = _tokenize(query)
        qfreq = _token_freq(query)
        scored = []
        for entry in self._entries:
            jaccard = _jaccard_similarity(qtokens, entry.tokens)
            cosine = _cosine_similarity(qfreq, entry.freq) if jaccard > 0 else 0
            combined = max(jaccard, cosine * 0.8)
            if combined > 0:
                scored.append((combined, entry))
        scored.sort(key=lambda x: -x[0])
        results = []
        for score, entry in scored[:top_k]:
            if score < 0.05:
                continue
            results.append({
                "id": entry.id,
                "text": entry.text[:200],
                "score": round(score, 4),
                "metadata": entry.metadata,
                "created_at": entry.created_at,
            })
        return results

    def delete(self, entry_id: str) -> bool:
        before = len(self._entries)
        self._entries = [e for e in self._entries if e.id != entry_id]
        if len(self._entries) < before:
            self._dirty = True
            return True
        return False

    def list_all(self, limit: int = 50) -> list[dict]:
        entries = sorted(self._entries, key=lambda e: e.created_at, reverse=True)
        return [e.to_dict() for e in entries[:limit]]

    def clear(self):
        self._entries.clear()
        self._dirty = True

    def count(self) -> int:
        return len(self._entries)

    def persist(self):
        if not self._dirty:
            return
        try:
            data = [(e.text, e.metadata, e.created_at, e.id) for e in self._entries]
            with open(VECTOR_STORE_PATH, "wb") as f:
                pickle.dump(data, f)
            self._dirty = False
        except Exception as e:
            info(f"Failed to save vector memory: {e}")

    def _load(self):
        if not os.path.exists(VECTOR_STORE_PATH):
            return
        try:
            with open(VECTOR_STORE_PATH, "rb") as f:
                data = pickle.load(f)
            for text, metadata, created_at, eid in data:
                entry = VectorEntry(text, metadata)
                entry.created_at = created_at
                entry.id = eid
                self._entries.append(entry)
            info(f"Loaded {len(self._entries)} vector memories")
        except Exception as e:
            info(f"Failed to load vector memory: {e}")
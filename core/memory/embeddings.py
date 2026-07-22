import os
import pickle
import time
import re
from typing import Any

from core.logger import info

MEMORY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "memory_store")
EMBEDDINGS_PATH = os.path.join(MEMORY_DIR, "embeddings.pkl")
os.makedirs(MEMORY_DIR, exist_ok=True)

_WORD_RE = re.compile(r"\w+")


class EmbeddingEntry:
    def __init__(self, text: str, metadata: dict | None = None):
        self.text = text
        self.metadata = metadata or {}
        self.created_at = time.time()
        self.id = self.metadata.get("id", str(time.time()))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "text": self.text[:300],
            "metadata": self.metadata,
            "created_at": self.created_at,
        }


class TfidfEngine:
    def __init__(self):
        self._entries: list[EmbeddingEntry] = []
        self._vectorizer = None
        self._matrix = None
        self._dirty = False
        self._needs_rebuild = False

    def store(self, text: str, metadata: dict | None = None) -> dict:
        entry = EmbeddingEntry(text, metadata)
        self._entries.append(entry)
        self._dirty = True
        self._needs_rebuild = True
        return {"id": entry.id, "text": text[:80], "success": True}

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        if not self._entries:
            return []
        if self._needs_rebuild:
            self._ensure_index()
            self._needs_rebuild = False
        if self._vectorizer is None or self._matrix is None:
            return []
        try:
            query_vec = self._vectorizer.transform([query])
            from sklearn.metrics.pairwise import cosine_similarity
            scores = cosine_similarity(query_vec, self._matrix)[0]
            scored = [(float(scores[i]), self._entries[i]) for i in range(len(self._entries))]
            scored.sort(key=lambda x: -x[0])
            results = []
            for score, entry in scored[:top_k]:
                if score < 0.05:
                    continue
                results.append({
                    "id": entry.id,
                    "text": entry.text[:300],
                    "score": round(score, 4),
                    "metadata": entry.metadata,
                    "created_at": entry.created_at,
                })
            return results
        except Exception as e:
            info(f"Embedding search error: {e}")
            return []

    def search_by_text(self, query: str, top_k: int = 5) -> list[dict]:
        return self.search(query, top_k)

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
        self._vectorizer = None
        self._matrix = None
        self._dirty = True

    def count(self) -> int:
        return len(self._entries)

    def get_entries(self) -> list[EmbeddingEntry]:
        return list(self._entries)

    def _ensure_index(self):
        if self._vectorizer is not None and not self._dirty:
            return
        if not self._entries:
            self._vectorizer = None
            self._matrix = None
            return
        from sklearn.feature_extraction.text import TfidfVectorizer
        texts = [e.text for e in self._entries]
        self._vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words="english",
            token_pattern=r"(?u)\b\w+\b",
        )
        self._matrix = self._vectorizer.fit_transform(texts)
        self._dirty = False

    def persist(self):
        try:
            data = [(e.text, e.metadata, e.created_at, e.id) for e in self._entries]
            with open(EMBEDDINGS_PATH, "wb") as f:
                pickle.dump(data, f)
        except Exception as e:
            info(f"Failed to save embeddings: {e}")

    def restore(self):
        if not os.path.exists(EMBEDDINGS_PATH):
            return
        try:
            with open(EMBEDDINGS_PATH, "rb") as f:
                data = pickle.load(f)
            for text, metadata, created_at, eid in data:
                entry = EmbeddingEntry(text, metadata)
                entry.created_at = created_at
                entry.id = eid
                self._entries.append(entry)
            self._dirty = True
            info(f"Restored {len(self._entries)} embedddings")
        except Exception as e:
            info(f"Failed to restore embeddings: {e}")


class SentenceEngine:
    _shared_model = None
    _model_ready = False
    _model_lock = None

    @classmethod
    def _init_lock(cls):
        if cls._model_lock is None:
            import threading
            cls._model_lock = threading.Lock()

    @classmethod
    def start_background_load(cls):
        cls._init_lock()
        import threading
        def _load():
            try:
                from sentence_transformers import SentenceTransformer
                model = SentenceTransformer("all-MiniLM-L6-v2")
                with cls._model_lock:
                    cls._shared_model = model
                    cls._model_ready = True
            except Exception:
                pass
        t = threading.Thread(target=_load, daemon=True)
        t.start()

    def __init__(self):
        self._entries: list[EmbeddingEntry] = []
        self._embeddings: list[list[float]] = []
        self._model = None
        self._dirty = False
        if SentenceEngine._model_ready:
            self._model = SentenceEngine._shared_model

    def _get_model(self):
        if self._model is not None:
            return self._model
        if SentenceEngine._model_ready:
            with SentenceEngine._model_lock:
                if SentenceEngine._model_ready:
                    self._model = SentenceEngine._shared_model
                    return self._model
        from sentence_transformers import SentenceTransformer
        self._model = SentenceTransformer("all-MiniLM-L6-v2")
        SentenceEngine._shared_model = self._model
        SentenceEngine._model_ready = True
        return self._model

    def store(self, text: str, metadata: dict | None = None) -> dict:
        entry = EmbeddingEntry(text, metadata)
        self._entries.append(entry)
        try:
            vec = self._get_model().encode([text])[0]
            self._embeddings.append(vec)
        except Exception:
            self._embeddings.append(None)
        self._dirty = True
        return {"id": entry.id, "text": text[:80], "success": True}

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        if not self._entries or not self._embeddings:
            return []
        try:
            import numpy as np
            query_vec = self._get_model().encode([query])[0]
            scores = []
            for i, emb in enumerate(self._embeddings):
                if emb is None:
                    continue
                sim = float(np.dot(query_vec, emb) / (np.linalg.norm(query_vec) * np.linalg.norm(emb)))
                scores.append((sim, self._entries[i]))
            scores.sort(key=lambda x: -x[0])
            results = []
            for score, entry in scores[:top_k]:
                if score < 0.3:
                    continue
                results.append({
                    "id": entry.id,
                    "text": entry.text[:300],
                    "score": round(score, 4),
                    "metadata": entry.metadata,
                    "created_at": entry.created_at,
                })
            return results
        except Exception as e:
            info(f"Sentence embedding search error: {e}")
            return []

    def search_by_text(self, query: str, top_k: int = 5) -> list[dict]:
        return self.search(query, top_k)

    def delete(self, entry_id: str) -> bool:
        before = len(self._entries)
        indices = [i for i, e in enumerate(self._entries) if e.id == entry_id]
        if not indices:
            return False
        idx = indices[0]
        self._entries.pop(idx)
        self._embeddings.pop(idx)
        return True

    def list_all(self, limit: int = 50) -> list[dict]:
        entries = sorted(self._entries, key=lambda e: e.created_at, reverse=True)
        return [e.to_dict() for e in entries[:limit]]

    def get_entries(self) -> list[EmbeddingEntry]:
        return list(self._entries)

    def clear(self):
        self._entries.clear()
        self._embeddings.clear()

    def persist(self):
        try:
            import numpy as np
            data = [(e.text, e.metadata, e.created_at, e.id) for e in self._entries]
            emb_data = [e.tolist() if isinstance(e, np.ndarray) else e for e in self._embeddings]
            with open(EMBEDDINGS_PATH, "wb") as f:
                pickle.dump({"entries": data, "embeddings": emb_data}, f)
        except Exception as e:
            info(f"Failed to save sentence embeddings: {e}")

    def restore(self):
        if not os.path.exists(EMBEDDINGS_PATH):
            return
        try:
            with open(EMBEDDINGS_PATH, "rb") as f:
                raw = pickle.load(f)
            data = raw if isinstance(raw, list) else raw.get("entries", [])
            for text, metadata, created_at, eid in data:
                entry = EmbeddingEntry(text, metadata)
                entry.created_at = created_at
                entry.id = eid
                self._entries.append(entry)
            if isinstance(raw, dict) and "embeddings" in raw:
                self._embeddings = raw["embeddings"]
            info(f"Restored {len(self._entries)} sentence embedddings")
        except Exception as e:
            info(f"Failed to restore sentence embeddings: {e}")


class EmbeddingEngine:
    def __init__(self):
        self._engine = None

    def _get_config_engine(self) -> str:
        try:
            from config.providers import get_provider_config
            cfg = get_provider_config("embeddings")
            return cfg.get("engine", "tfidf").lower()
        except Exception:
            import os as _os
            return _os.environ.get("FRIDAY_EMBEDDINGS", "tfidf").lower()

    def _ensure(self):
        if self._engine is not None:
            return self._engine
        use_st = self._get_config_engine() == "sentence"
        if use_st:
            try:
                self._engine = SentenceEngine()
                self._engine.restore()
                info("Using sentence-transformers embedding engine")
                return self._engine
            except Exception as e:
                info(f"Failed to init sentence-transformers: {e}, falling back to TF-IDF")
        self._engine = TfidfEngine()
        self._engine.restore()
        info("Using TF-IDF embedding engine (set FRIDAY_EMBEDDINGS=sentence to upgrade)")
        return self._engine

    def store(self, text: str, metadata: dict | None = None) -> dict:
        return self._ensure().store(text, metadata)

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        return self._ensure().search(query, top_k)

    def delete(self, entry_id: str) -> bool:
        return self._ensure().delete(entry_id)

    def list_all(self, limit: int = 50) -> list[dict]:
        return self._ensure().list_all(limit)

    def clear(self):
        self._ensure().clear()

    def count(self) -> int:
        return self._ensure().count()

    def get_entries(self) -> list[EmbeddingEntry]:
        return self._ensure().get_entries()

    def persist(self):
        self._ensure().persist()
        if hasattr(self._engine, '_dirty'):
            self._engine._dirty = False

    def is_dirty(self) -> bool:
        self._ensure()
        return getattr(self._engine, '_dirty', False)

    def get_engine_type(self) -> str:
        self._ensure()
        if isinstance(self._engine, SentenceEngine):
            return "sentence-transformers"
        if isinstance(self._engine, TfidfEngine):
            return "tfidf"
        return "none"

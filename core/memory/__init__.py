import os
import time
from typing import Any

from core.memory.working import WorkingMemory
from core.memory.long_term import LongTermMemory
from core.memory.conversation import ConversationMemory
from core.memory.vector import VectorMemory
from core.memory.embeddings import EmbeddingEngine
from core.memory.consolidator import MemoryConsolidator
from core.logger import info

MEMORY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "memory_store")
os.makedirs(MEMORY_DIR, exist_ok=True)

_working = WorkingMemory()
_long_term = LongTermMemory(os.path.join(MEMORY_DIR, "long_term.json"))
_conversation = ConversationMemory(max_tokens=4000)
_vector = VectorMemory()
_embeddings = EmbeddingEngine()


class MemoryManager:
    def __init__(self):
        self.working = _working
        self.long_term = _long_term
        self.conversation = _conversation
        self.vector = _vector
        self.embeddings = _embeddings
        self.consolidator = MemoryConsolidator(self)

    def store(self, key: str, value: Any, importance: float = 0.5) -> dict:
        self.working.set(key, value)
        result = self.long_term.store(key, value, importance)
        self.embeddings.store(f"{key}: {value}", {"key": key, "importance": importance})
        self.vector.store(f"{key}: {value}", {"key": key, "importance": importance})
        return result

    def recall(self, key: str) -> dict:
        result = self.working.get(key)
        if result is not None:
            return {"key": key, "value": result, "source": "working"}
        return self.long_term.recall(key)

    def forget(self, key: str) -> dict:
        self.working.delete(key)
        return self.long_term.forget(key)

    def list_all(self) -> dict:
        return self.long_term.list_all()

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        import concurrent.futures
        seen_ids: set[str] = set()
        merged: list[dict] = []

        def _keyword_search() -> list[dict]:
            q = query.lower()
            entries = self.long_term.list_all().get("entries", [])
            scored = []
            for e in entries:
                val = str(e.get("value", "")).lower()
                key = str(e.get("key", "")).lower()
                score = val.count(q) + key.count(q) * 2
                if score:
                    scored.append((score, e))
            scored.sort(key=lambda x: -x[0])
            kw_results = []
            for _, e in scored[:top_k]:
                kw_results.append({
                    "id": e.get("key", ""),
                    "text": str(e.get("value", ""))[:200],
                    "score": 0.3,
                    "metadata": {"source": "long_term"},
                })
            return kw_results

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            embed_fut = pool.submit(self.embeddings.search, query, top_k)
            vector_fut = pool.submit(self.vector.search, query, top_k)
            keyword_fut = pool.submit(_keyword_search)

            for future in concurrent.futures.as_completed([embed_fut, vector_fut, keyword_fut]):
                for r in future.result():
                    rid = r.get("id", "")
                    if rid not in seen_ids:
                        seen_ids.add(rid)
                        merged.append(r)

        merged.sort(key=lambda x: -x.get("score", 0))
        return merged[:top_k]

    def add_conversation(self, role: str, content: str):
        self.conversation.add(role, content)

    def get_conversation_summary(self) -> str:
        return self.conversation.summarize()

    def run_maintenance(self):
        self.long_term.decay()
        self.conversation.compress()
        self.consolidator.run_cycle()
        self.vector.persist()
        self.long_term.persist()
        self.embeddings.persist()

    def store_conversation_memory(self, user_input: str, response: str):
        summary = f"User asked: {user_input[:120]}. Assistant responded: {response[:200]}"
        self.embeddings.store(summary, {"type": "conversation", "user_input": user_input[:200]})
        self.vector.store(summary, {"type": "conversation", "user_input": user_input[:200]})
        self.long_term.store(f"conv_{int(time.time())}", summary, importance=0.3)

    def inject_context(self, user_input: str, max_memories: int = 5) -> str:
        relevant = self.embeddings.search(user_input, top_k=max_memories)
        if not relevant:
            relevant = self.vector.search(user_input, top_k=max_memories)
        if not relevant:
            return ""
        ctx_lines = ["Relevant past context:"]
        for r in relevant:
            ctx_lines.append(f"- {r['text']}")
        return "\n".join(ctx_lines)


_manager = MemoryManager()


def get_memory_manager() -> MemoryManager:
    return _manager

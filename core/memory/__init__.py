import os
from typing import Any

from core.memory.working import WorkingMemory
from core.memory.long_term import LongTermMemory
from core.memory.conversation import ConversationMemory
from core.logger import info

MEMORY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "memory_store")
os.makedirs(MEMORY_DIR, exist_ok=True)

_working = WorkingMemory()
_long_term = LongTermMemory(os.path.join(MEMORY_DIR, "long_term.json"))
_conversation = ConversationMemory(max_tokens=4000)


class MemoryManager:
    def __init__(self):
        self.working = _working
        self.long_term = _long_term
        self.conversation = _conversation

    def store(self, key: str, value: Any, importance: float = 0.5) -> dict:
        self.working.set(key, value)
        return self.long_term.store(key, value, importance)

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
        results = [e for _, e in scored[:top_k]]
        return results

    def add_conversation(self, role: str, content: str):
        self.conversation.add(role, content)

    def get_conversation_summary(self) -> str:
        return self.conversation.summarize()

    def run_maintenance(self):
        self.long_term.decay()
        self.conversation.compress()


_manager = MemoryManager()


def get_memory_manager() -> MemoryManager:
    return _manager

import time
from typing import Any


class ConversationMemory:
    def __init__(self, max_tokens: int = 4000):
        self._messages: list[dict[str, Any]] = []
        self._max_tokens = max_tokens
        self._summaries: list[str] = []

    def add(self, role: str, content: str):
        self._messages.append({
            "role": role,
            "content": content,
            "timestamp": time.time(),
        })
        self._trim()

    def get_messages(self) -> list[dict]:
        return list(self._messages)

    def clear(self):
        self._messages.clear()

    def _trim(self):
        total = sum(len(m.get("content", "")) for m in self._messages)
        while total > self._max_tokens * 4 and len(self._messages) > 10:
            removed = self._messages.pop(0)
            total -= len(removed.get("content", ""))

    def summarize(self) -> str:
        if not self._summaries:
            return ""
        return " | ".join(self._summaries[-3:])

    def compress(self):
        if len(self._messages) > 50:
            old = self._messages[:-20]
            self._summaries.append(f"Earlier conversation had {len(old)} messages")
            self._messages = self._messages[-20:]

import json
import os
from datetime import datetime, timezone
from typing import Any

SESSION_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "sessions")
os.makedirs(SESSION_DIR, exist_ok=True)


class Session:
    def __init__(self, language: str = "english"):
        self.session_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.language = language
        self.messages: list[dict[str, Any]] = []
        self.metadata: dict[str, Any] = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "language": language,
            "message_count": 0,
        }

    def add_message(self, role: str, content: str, **extra):
        entry = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **extra,
        }
        self.messages.append(entry)
        self.metadata["message_count"] = len(self.messages)

    def clear(self):
        self.messages.clear()
        self.metadata["message_count"] = 0

    def export_json(self) -> str:
        data = {
            "session_id": self.session_id,
            "metadata": self.metadata,
            "messages": self.messages,
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    def export_markdown(self) -> str:
        lines = [
            f"# Session: {self.session_id}",
            f"Language: {self.language}",
            f"Messages: {len(self.messages)}",
            "",
            "---",
            "",
        ]
        for msg in self.messages:
            role = msg["role"].upper()
            content = msg["content"]
            if role == "SYSTEM":
                continue
            lines.append(f"### {role}")
            lines.append("")
            lines.append(content)
            lines.append("")
        return "\n".join(lines)

    def save(self):
        path = os.path.join(SESSION_DIR, f"session_{self.session_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.export_json())
        return path

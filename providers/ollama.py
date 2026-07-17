import json
import time
from typing import Any, Generator

import ollama

from providers.base import BaseProvider
from providers.registry import register_provider


class OllamaProvider(BaseProvider):
    @property
    def name(self) -> str:
        return "ollama"

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self._client = ollama.Client(
            host=config.get("base_url", "http://localhost:11434")
        )

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> Generator[dict, None, None]:
        model = self.config.get("model", "qwen2.5:3b")
        temperature = self.config.get("temperature", 0.7)
        max_tokens = self.config.get("max_tokens", 2048)

        stream = self._client.chat(
            model=model,
            messages=messages,
            tools=tools,
            stream=True,
            options={
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        )

        buffer = []
        last_flush = time.monotonic()
        content_parts = []
        tool_calls = None

        for chunk in stream:
            delta = chunk.get("message", {})

            if "content" in delta and delta["content"]:
                buffer.append(delta["content"])
                content_parts.append(delta["content"])
                now = time.monotonic()
                if now - last_flush >= 0.05 or len(buffer) >= 5:
                    text = "".join(buffer)
                    buffer.clear()
                    last_flush = now
                    yield {"type": "tokens", "content": text}

            if "tool_calls" in delta and delta["tool_calls"]:
                raw = delta["tool_calls"]
                normalized = []
                for tc in raw:
                    fn = tc.get("function", tc.function if hasattr(tc, "function") else {})
                    name = fn.get("name", fn.name if hasattr(fn, "name") else "?")
                    args = fn.get("arguments", fn.arguments if hasattr(fn, "arguments") else {})
                    tc_id = tc.get("id", getattr(tc, "id", ""))
                    if isinstance(args, dict):
                        args = json.dumps(args, ensure_ascii=False)
                    normalized.append({
                        "id": tc_id,
                        "type": "function",
                        "function": {"name": name, "arguments": args},
                    })
                tool_calls = normalized

        if buffer:
            yield {"type": "tokens", "content": "".join(buffer)}

        yield {"type": "done", "content": "".join(content_parts), "tool_calls": tool_calls}


register_provider("ollama", OllamaProvider)

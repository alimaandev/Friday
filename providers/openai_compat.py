import time
from typing import Any, Generator

from openai import OpenAI, APIError, APIConnectionError, APITimeoutError, RateLimitError
import httpx

from providers.base import BaseProvider
from providers.registry import register_provider


def _is_retryable_err(e: Exception) -> bool:
    msg = str(e).lower()
    if any(x in msg for x in ["deadline", "timeout", "timed out", "too many requests", "rate limit"]):
        return True
    # curl error 16 = CURLE_HTTP2_ERROR — HTTP/2 framing failure
    if "curl: (16)" in msg or "http2" in msg or "http/2" in msg:
        return True
    return False


class OpenAICompatibleProvider(BaseProvider):
    @property
    def name(self) -> str:
        return self.config.get("provider_name", "openai")

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self._client = None

    def _get_client(self) -> OpenAI:
        if self._client is not None:
            return self._client
        api_key = self.config.get("api_key", "") or ""
        base_url = self.config.get("base_url", "https://api.openai.com/v1")
        timeout = self.config.get("timeout", 30)
        http_client = httpx.Client(http2=False, timeout=httpx.Timeout(timeout))
        self._client = OpenAI(api_key=api_key, base_url=base_url, http_client=http_client)
        return self._client

    def _stream(
        self, model: str, messages: list[dict], tools: list[dict] | None, temperature: float, max_tokens: int,
    ) -> Generator[dict, None, None]:
        kwargs = dict(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            stream_options={"include_usage": True},
        )
        if tools:
            kwargs["tools"] = tools

        client = self._get_client()
        stream = client.chat.completions.create(**kwargs)

        buffer: list[str] = []
        last_flush = time.monotonic()
        content_parts: list[str] = []
        tool_calls_acc: dict[int, dict] = {}

        for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta
            if not delta:
                continue

            if delta.content:
                buffer.append(delta.content)
                content_parts.append(delta.content)
                now = time.monotonic()
                if now - last_flush >= 0.05 or len(buffer) >= 5:
                    yield {"type": "tokens", "content": "".join(buffer)}
                    buffer.clear()
                    last_flush = now

            if delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in tool_calls_acc:
                        tool_calls_acc[idx] = {
                            "id": tc.id or "",
                            "type": "function",
                            "function": {"name": "", "arguments": ""},
                        }
                    if tc.function:
                        if tc.function.name:
                            tool_calls_acc[idx]["function"]["name"] += tc.function.name
                        if tc.function.arguments:
                            tool_calls_acc[idx]["function"]["arguments"] += tc.function.arguments

        if buffer:
            yield {"type": "tokens", "content": "".join(buffer)}

        tool_calls = (
            [v for _, v in sorted(tool_calls_acc.items())]
            if tool_calls_acc
            else None
        )

        yield {
            "type": "done",
            "content": "".join(content_parts),
            "tool_calls": tool_calls,
        }

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> Generator[dict, None, None]:
        model = self.config.get("model", "gpt-4o")
        fallback = self.config.get("fallback_model", "openai/gpt-4o-mini")
        temperature = self.config.get("temperature", 0.7)
        max_tokens = self.config.get("max_tokens", 4096)

        attempts = [(model, False), (fallback, True)]
        for attempt_model, is_fallback in attempts:
            try:
                yield from self._stream(attempt_model, messages, tools, temperature, max_tokens)
                return
            except Exception as e:
                err_msg = str(e)
                if is_fallback or not _is_retryable_err(e):
                    yield {"type": "done", "content": f"Error: {err_msg}", "final": True}
                    return
                yield {"type": "tokens", "content": f"[Primary model failed ({err_msg[:60]}), retrying with {fallback}…]\n\n"}


register_provider("openai", OpenAICompatibleProvider)
register_provider("openrouter", OpenAICompatibleProvider)
register_provider("openai_compatible", OpenAICompatibleProvider)

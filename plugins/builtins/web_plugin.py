import urllib.request
import urllib.error
import socket
import re

from plugins.base import ToolPlugin


def _strip_html(html: str) -> str:
    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


class WebFetchPlugin(ToolPlugin):
    name = "web_fetch"
    description = "Fetch and extract text content from a URL"
    category = "web"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The URL to fetch"},
            },
            "required": ["url"],
        }

    def execute(self, url: str, timeout: int = 15) -> dict:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                content = response.read().decode("utf-8", errors="replace")
            text = _strip_html(content)
            return {"content": text[:5000], "error": None}
        except (urllib.error.URLError, socket.timeout, ValueError) as e:
            return {"content": None, "error": str(e)}

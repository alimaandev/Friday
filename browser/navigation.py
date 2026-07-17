import time
import urllib.parse

from browser.browser import get_browser
from core.logger import info


def search(query: str, engine: str = "google") -> dict:
    page = get_browser().get_page()
    engines = {
        "google": "https://www.google.com/search?q={}",
        "bing": "https://www.bing.com/search?q={}",
        "duckduckgo": "https://duckduckgo.com/?q={}",
    }
    template = engines.get(engine, engines["google"])
    url = template.format(urllib.parse.quote(query))
    result = _go(page, url)
    if result.get("status") == "success":
        try:
            text = page.locator("body").inner_text(timeout=5000)
            result["text"] = text[:5000]
        except Exception as e:
            result["text"] = f"(could not extract page text: {e})"
    return result


def navigate(url: str) -> dict:
    page = get_browser().get_page()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return _go(page, url)


def _go(page, url: str) -> dict:
    for attempt in range(2):
        try:
            page.goto(url, wait_until="load", timeout=30000)
            page.bring_to_front()
            if page.url == "about:blank" or page.url.startswith("about:"):
                time.sleep(1)
                continue
            return {
                "url": page.url,
                "title": page.title(),
                "status": "success",
            }
        except Exception as e:
            if attempt == 1:
                info(f"Navigation failed (attempt {attempt + 1}): {e}")
                return {"url": url, "error": str(e), "status": "error"}
            time.sleep(1)
    return {"url": url, "error": "Navigation failed after retries", "status": "error"}

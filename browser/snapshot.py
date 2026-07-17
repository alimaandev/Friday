import os
import time
from datetime import datetime

from browser.browser import get_browser, SCREENSHOT_DIR


def get_text(selector: str) -> dict:
    page = get_browser().get_page()
    try:
        loc = page.locator(selector)
        text = loc.inner_text(timeout=5000)
        return {"selector": selector, "text": text[:2000]}
    except Exception as e:
        return {"selector": selector, "error": str(e)}


def get_page_text() -> dict:
    page = get_browser().get_page()
    try:
        text = page.locator("body").inner_text()
        return {
            "text": text[:5000],
            "url": page.url,
            "title": page.title(),
        }
    except Exception as e:
        return {"error": str(e)}


def screenshot() -> dict:
    page = get_browser().get_page()
    try:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fpath = os.path.join(SCREENSHOT_DIR, f"screenshot_{ts}.png")
        page.screenshot(path=fpath, full_page=True)
        return {"path": fpath.replace("\\", "/"), "url": page.url}
    except Exception as e:
        return {"error": str(e)}


def scroll(x: int = 0, y: int = 500) -> dict:
    page = get_browser().get_page()
    try:
        page.evaluate(f"window.scrollBy({{top: {y}, left: {x}, behavior: 'smooth'}})")
        return {"x": x, "y": y, "status": "scrolled"}
    except Exception as e:
        return {"x": x, "y": y, "error": str(e), "status": "error"}


def wait(ms: int = 1000) -> dict:
    get_browser().get_page()
    time.sleep(ms / 1000)
    return {"waited_ms": ms, "status": "done"}

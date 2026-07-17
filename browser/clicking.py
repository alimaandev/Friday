from browser.browser import get_browser
from core.logger import info


_CLICK_STRATEGIES = ["text", "role", "css", "coords"]


def smart_click(target: str, strategy: str = "auto") -> dict:
    page = get_browser().get_page()
    strategies = _CLICK_STRATEGIES if strategy == "auto" else [strategy]

    for strat in strategies:
        try:
            if strat == "text":
                for exact in [True, False]:
                    try:
                        loc = page.get_by_text(target, exact=exact)
                        loc.first.wait_for(timeout=3000)
                        loc.first.click(timeout=3000)
                        page.bring_to_front()
                        return {"status": "clicked", "strategy": "text", "target": target}
                    except Exception:
                        continue
            elif strat == "role":
                loc = page.get_by_role(target)
                loc.first.wait_for(timeout=3000)
                loc.first.click(timeout=3000)
                page.bring_to_front()
                return {"status": "clicked", "strategy": "role", "target": target}
            elif strat == "css":
                loc = page.locator(target)
                loc.wait_for(timeout=3000)
                loc.click(timeout=3000)
                page.bring_to_front()
                return {"status": "clicked", "strategy": "css", "target": target}
            elif strat == "coords":
                parts = target.split(",")
                x, y = int(parts[0]), int(parts[1])
                page.mouse.move(x, y)
                page.mouse.click(x, y)
                page.bring_to_front()
                return {"status": "clicked", "strategy": "coords", "target": target}
        except Exception as e:
            continue

    return {"status": "error", "error": f"Could not click '{target}' with any strategy", "target": target}


def click_text(text: str) -> dict:
    page = get_browser().get_page()
    for exact in [True, False]:
        try:
            loc = page.get_by_text(text, exact=exact)
            loc.first.wait_for(timeout=5000)
            loc.first.click(timeout=5000)
            page.bring_to_front()
            return {"text": text, "method": "text", "status": "clicked"}
        except Exception:
            continue
    return {"text": text, "error": f"No element with text: {text}", "status": "error"}


def click_role(role: str, name: str = "") -> dict:
    page = get_browser().get_page()
    try:
        loc = page.get_by_role(role, name=name) if name else page.get_by_role(role)
        loc.first.wait_for(timeout=10000)
        loc.first.click(timeout=5000)
        page.bring_to_front()
        return {"role": role, "name": name, "method": "role", "status": "clicked"}
    except Exception as e:
        return {"role": role, "name": name, "error": str(e), "status": "error"}


def click_coords(x: int, y: int) -> dict:
    page = get_browser().get_page()
    try:
        page.mouse.move(x, y)
        page.mouse.click(x, y)
        page.bring_to_front()
        return {"x": x, "y": y, "method": "coords", "status": "clicked"}
    except Exception as e:
        return {"x": x, "y": y, "error": str(e), "status": "error"}


def hover(selector: str) -> dict:
    page = get_browser().get_page()
    try:
        loc = page.locator(selector)
        loc.wait_for(timeout=10000)
        loc.hover()
        page.bring_to_front()
        return {"selector": selector, "status": "hovered"}
    except Exception as e:
        return {"selector": selector, "error": str(e), "status": "error"}

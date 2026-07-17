from browser.browser import get_browser


def type_text(selector: str, text: str) -> dict:
    page = get_browser().get_page()
    try:
        loc = page.locator(selector)
        loc.wait_for(timeout=10000)
        loc.click()
        loc.fill(text)
        page.bring_to_front()
        return {"selector": selector, "method": "css", "status": "typed"}
    except Exception as e:
        return {"selector": selector, "error": str(e), "status": "error"}


def type_by_label(label: str, text: str) -> dict:
    page = get_browser().get_page()
    try:
        loc = page.get_by_label(label)
        loc.wait_for(timeout=10000)
        loc.click()
        loc.fill(text)
        page.bring_to_front()
        return {"label": label, "method": "label", "status": "typed"}
    except Exception as e:
        return {"label": label, "error": str(e), "status": "error"}


def press_key(key: str) -> dict:
    page = get_browser().get_page()
    try:
        page.keyboard.press(key)
        page.bring_to_front()
        return {"key": key, "status": "pressed"}
    except Exception as e:
        return {"key": key, "error": str(e), "status": "error"}

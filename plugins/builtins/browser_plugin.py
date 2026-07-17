from browser import (
    search, navigate, smart_click, click_text, click_role, click_coords,
    type_text, type_by_label, press_key, hover, scroll,
    get_text, get_page_text, screenshot, wait,
)
from plugins.base import ToolPlugin


class BrowseSearchPlugin(ToolPlugin):
    name = "browse_search"
    description = "Search the web using a search engine. Goes directly to the search results page - no CAPTCHA."
    category = "browser"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"},
                "engine": {"type": "string", "description": "Search engine: google, bing, duckduckgo (default: google)"},
            },
            "required": ["query"],
        }

    def execute(self, query: str, engine: str = "google") -> dict:
        return search(query, engine)


class BrowseNavigatePlugin(ToolPlugin):
    name = "browse_navigate"
    description = "Open a URL in the browser. The browser opens in a visible Chrome window."
    category = "browser"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to navigate to"},
            },
            "required": ["url"],
        }

    def execute(self, url: str) -> dict:
        return navigate(url)


class BrowseClickPlugin(ToolPlugin):
    name = "browse_click"
    description = "Click an element using a CSS selector. Uses real mouse movement and click."
    category = "browser"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "CSS selector of element to click"},
            },
            "required": ["selector"],
        }

    def execute(self, selector: str) -> dict:
        return smart_click(selector, strategy="css")


class BrowseClickTextPlugin(ToolPlugin):
    name = "browse_click_text"
    description = "Click an element by its visible text. Best for buttons, links, and labeled UI elements."
    category = "browser"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The visible text of the element to click"},
            },
            "required": ["text"],
        }

    def execute(self, text: str) -> dict:
        return click_text(text)


class BrowseClickRolePlugin(ToolPlugin):
    name = "browse_click_role"
    description = "Click an element by its ARIA role (button, link, textbox, checkbox, etc.)"
    category = "browser"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "role": {"type": "string", "description": "ARIA role: button, link, textbox, checkbox, radio, heading"},
                "name": {"type": "string", "description": "Accessible name of the element (optional)"},
            },
            "required": ["role"],
        }

    def execute(self, role: str, name: str = "") -> dict:
        return click_role(role, name)


class BrowseClickCoordsPlugin(ToolPlugin):
    name = "browse_click_coords"
    description = "Click at specific pixel coordinates on the page."
    category = "browser"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "X coordinate in pixels"},
                "y": {"type": "integer", "description": "Y coordinate in pixels"},
            },
            "required": ["x", "y"],
        }

    def execute(self, x: int, y: int) -> dict:
        return click_coords(x, y)


class BrowseTypePlugin(ToolPlugin):
    name = "browse_type"
    description = "Type text into an input field using a CSS selector. Clicks the field first, then types."
    category = "browser"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "CSS selector of the input field"},
                "text": {"type": "string", "description": "Text to type into the field"},
            },
            "required": ["selector", "text"],
        }

    def execute(self, selector: str, text: str) -> dict:
        return type_text(selector, text)


class BrowseTypeByLabelPlugin(ToolPlugin):
    name = "browse_type_by_label"
    description = "Type text into an input field identified by its label text. Best for forms with visible labels."
    category = "browser"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "label": {"type": "string", "description": "The label text of the input field"},
                "text": {"type": "string", "description": "Text to type"},
            },
            "required": ["label", "text"],
        }

    def execute(self, label: str, text: str) -> dict:
        return type_by_label(label, text)


class BrowsePressKeyPlugin(ToolPlugin):
    name = "browse_press_key"
    description = "Press a keyboard key (Enter, Escape, ArrowDown, Tab, Backspace)"
    category = "browser"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Key name to press (Enter, Escape, Tab, ArrowDown, etc.)"},
            },
            "required": ["key"],
        }

    def execute(self, key: str) -> dict:
        return press_key(key)


class BrowseHoverPlugin(ToolPlugin):
    name = "browse_hover"
    description = "Move the mouse over an element identified by CSS selector. Useful for tooltips and dropdown menus."
    category = "browser"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "CSS selector of element to hover over"},
            },
            "required": ["selector"],
        }

    def execute(self, selector: str) -> dict:
        return hover(selector)


class BrowseScrollPlugin(ToolPlugin):
    name = "browse_scroll"
    description = "Scroll the page by a given number of pixels. Default scrolls down 500px."
    category = "browser"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "Horizontal scroll in pixels (default: 0)"},
                "y": {"type": "integer", "description": "Vertical scroll in pixels (default: 500)"},
            },
            "required": [],
        }

    def execute(self, x: int = 0, y: int = 500) -> dict:
        return scroll(x, y)


class BrowseGetTextPlugin(ToolPlugin):
    name = "browse_get_text"
    description = "Get text content from a specific element on the page"
    category = "browser"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "CSS selector of the element"},
            },
            "required": ["selector"],
        }

    def execute(self, selector: str) -> dict:
        return get_text(selector)


class BrowseGetPageTextPlugin(ToolPlugin):
    name = "browse_get_page_text"
    description = "Get all visible text from the current page"
    category = "browser"

    def get_parameters_schema(self):
        return {"type": "object", "properties": {}, "required": []}

    def execute(self) -> dict:
        return get_page_text()


class BrowseScreenshotPlugin(ToolPlugin):
    name = "browse_screenshot"
    description = "Take a screenshot of the current browser page. Saves to screenshots/ folder."
    category = "browser"

    def get_parameters_schema(self):
        return {"type": "object", "properties": {}, "required": []}

    def execute(self) -> dict:
        return screenshot()


class BrowseWaitPlugin(ToolPlugin):
    name = "browse_wait"
    description = "Wait for a specified number of milliseconds. Use this to let pages load or animations complete."
    category = "browser"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "ms": {"type": "integer", "description": "Milliseconds to wait (default: 1000)"},
            },
            "required": [],
        }

    def execute(self, ms: int = 1000) -> dict:
        return wait(ms)

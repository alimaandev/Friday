from typing import Any

from core.computer import get_computer_control
from plugins.base import ToolPlugin


class OpenAppPlugin(ToolPlugin):
    name = "open_app"
    description = (
        "Open an application on the desktop by name or path (e.g. 'notepad', 'chrome'). "
        "Powerful — confirm with the user before executing."
    )
    category = "control"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {"app": {"type": "string", "description": "Application name or path to open"}},
            "required": ["app"],
        }

    def execute(self, app: str) -> dict[str, Any]:
        return get_computer_control().open_app(app)


class FocusWindowPlugin(ToolPlugin):
    name = "focus_window"
    description = "Bring a window matching a title fragment to the foreground (Windows)."
    category = "control"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {"title": {"type": "string", "description": "Window title fragment to focus"}},
            "required": ["title"],
        }

    def execute(self, title: str) -> dict[str, Any]:
        return get_computer_control().focus_window(title)


class TypeTextPlugin(ToolPlugin):
    name = "type_text"
    description = (
        "Type a string of text as if it were typed at the keyboard into the currently focused application. "
        "Requires user confirmation."
    )
    category = "control"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {"text": {"type": "string", "description": "Text to type"}},
            "required": ["text"],
        }

    def execute(self, text: str) -> dict[str, Any]:
        return get_computer_control().type_text(text)


class PressKeyPlugin(ToolPlugin):
    name = "press_key"
    description = "Press a single keyboard key (e.g. 'enter', 'tab', 'ctrl', 'esc') in the focused application."
    category = "control"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {"key": {"type": "string", "description": "Key name to press"}},
            "required": ["key"],
        }

    def execute(self, key: str) -> dict[str, Any]:
        return get_computer_control().press_key(key)


class ClickMousePlugin(ToolPlugin):
    name = "click_mouse"
    description = "Click at absolute screen coordinates. Requires user confirmation."
    category = "control"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "X coordinate"},
                "y": {"type": "integer", "description": "Y coordinate"},
                "button": {
                    "type": "string",
                    "description": "Mouse button (left, right, middle)",
                    "enum": ["left", "right", "middle"],
                },
            },
            "required": ["x", "y"],
        }

    def execute(self, x: int, y: int, button: str = "left") -> dict[str, Any]:
        return get_computer_control().click(int(x), int(y), button=button)


class GetCursorPlugin(ToolPlugin):
    name = "get_cursor"
    description = "Get the current mouse cursor position on screen."
    category = "control"

    def get_parameters_schema(self):
        return {"type": "object", "properties": {}, "required": []}

    def execute(self) -> dict[str, Any]:
        return get_computer_control().get_cursor()


class GetScreenSizePlugin(ToolPlugin):
    name = "get_screen_size"
    description = "Get the screen resolution (width x height)."
    category = "control"

    def get_parameters_schema(self):
        return {"type": "object", "properties": {}, "required": []}

    def execute(self) -> dict[str, Any]:
        return get_computer_control().screen_size()

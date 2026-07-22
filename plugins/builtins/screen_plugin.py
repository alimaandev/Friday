import base64
import io
import time
from typing import Any

from PIL import Image, ImageGrab

from plugins.base import ToolPlugin


def _capture(region: tuple[int, int, int, int] | None = None) -> bytes:
    img = ImageGrab.grab(bbox=region)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def _get_window_titles() -> list[dict]:
    titles = []
    try:
        import win32gui

        def cb(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    titles.append({"handle": hwnd, "title": title})
        win32gui.EnumWindows(cb, None)
    except ImportError:
        pass
    return titles


class ScreenCapturePlugin(ToolPlugin):
    name = "capture_screen"
    description = "Capture the current desktop screen as a base64 PNG image. Returns image data and basic screen info."
    category = "screen"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "left": {"type": "integer", "description": "Left coordinate of region to capture (optional)"},
                "top": {"type": "integer", "description": "Top coordinate of region (optional)"},
                "right": {"type": "integer", "description": "Right coordinate of region (optional)"},
                "bottom": {"type": "integer", "description": "Bottom coordinate of region (optional)"},
            },
            "required": [],
        }

    def execute(self, left: int | None = None, top: int | None = None,
                right: int | None = None, bottom: int | None = None) -> dict[str, Any]:
        region = (left, top, right, bottom) if all(x is not None for x in [left, top, right, bottom]) else None
        try:
            from PIL import Image
            img = ImageGrab.grab(bbox=region)
            buf = io.BytesIO()
            img.save(buf, format="PNG", optimize=True)
            b64 = base64.b64encode(buf.getvalue()).decode()
            return {
                "image": b64,
                "format": "PNG",
                "width": img.width,
                "height": img.height,
                "timestamp": time.time(),
            }
        except Exception as e:
            return {"error": str(e)}


class ListWindowsPlugin(ToolPlugin):
    name = "list_windows"
    description = "List all visible open windows on the desktop with their titles."
    category = "screen"

    def get_parameters_schema(self):
        return {"type": "object", "properties": {}, "required": []}

    def execute(self) -> dict[str, Any]:
        titles = _get_window_titles()
        return {"windows": titles, "count": len(titles)}


class AnalyzeScreenPlugin(ToolPlugin):
    name = "analyze_screen"
    description = "Capture the screen and ask a question about what's visible. Only works if the AI provider supports vision (image understanding)."
    category = "screen"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "Question about what's on screen"},
            },
            "required": ["question"],
        }

    def execute(self, question: str) -> dict[str, Any]:
        try:
            data = _capture()
            b64 = base64.b64encode(data).decode()
            return {
                "image_data": b64,
                "image_size": len(data),
                "image_format": "PNG",
                "width": ImageGrab.grab().width,
                "height": ImageGrab.grab().height,
                "question": question,
                "note": "The image_data is a full base64 PNG. Pass it to a vision-capable model for analysis. If the model does not support vision, describe what might be visible based on context.",
            }
        except Exception as e:
            return {"error": str(e)}

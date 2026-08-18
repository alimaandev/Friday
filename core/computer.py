"""Computer Control — Friday drives the user's desktop.

Wraps cross-platform automation so the orb can open apps, type, click, and
read the screen. On Windows it uses ``pyautogui`` (input) and ``pywin32``
(window focus). Every capability degrades gracefully when the dependency is
missing so discovery never breaks the tool chain.

The layer returns plain dicts — safe to hand straight to a ToolPlugin.
"""

import os
import platform
import shutil
import subprocess

import core.logger as logger

_IS_WINDOWS = platform.system() == "Windows"


class ComputerControl:
    def __init__(self):
        self._pyautogui = None
        self._win32gui = None
        self._load()

    def _load(self):
        try:
            import pyautogui

            self._pyautogui = pyautogui
        except Exception:
            logger.warn("pyautogui not available — mouse/keyboard control disabled")
        try:
            import win32gui

            self._win32gui = win32gui
        except Exception:
            self._win32gui = None

    @property
    def available(self) -> dict:
        return {
            "platform": platform.system(),
            "mouse_keyboard": self._pyautogui is not None,
            "window_management": self._win32gui is not None,
            "note": "pip install pyautogui pywin32 to enable full desktop control",
        }

    # ──────────────── Windows ──────────────────────────────────────────────────

    def list_windows(self) -> dict:
        if self._win32gui is None:
            return {"windows": [], "error": "pywin32 not available (Windows only)"}
        titles = []

        def _cb(hwnd, _):
            if self._win32gui.IsWindowVisible(hwnd):
                title = self._win32gui.GetWindowText(hwnd)
                if title:
                    titles.append({"handle": hwnd, "title": title})

        self._win32gui.EnumWindows(_cb, None)
        return {"windows": titles, "count": len(titles)}

    def close_app(self, name: str) -> dict:
        """Close an application by window title fragment (Windows)."""
        if self._win32gui is None:
            return {"success": False, "error": "pywin32 not available (Windows only)"}

        def _cb(hwnd, _):
            if self._win32gui.IsWindowVisible(hwnd) and name.lower() in self._win32gui.GetWindowText(hwnd).lower():
                try:
                    self._win32gui.PostMessage(hwnd, 0x0010, 0, 0)  # WM_CLOSE
                    _cb.closed = True
                except Exception:
                    pass
            return True

        _cb.closed = False
        self._win32gui.EnumWindows(_cb, None)
        if getattr(_cb, "closed", False):
            return {"success": True, "app": name}
        return {"success": False, "error": f"No visible window matched '{name}'"}

    def focus_window(self, title: str) -> dict:
        if self._win32gui is None:
            return {"success": False, "error": "pywin32 not available (Windows only)"}

        def _cb(hwnd, _):
            if self._win32gui.IsWindowVisible(hwnd) and title.lower() in self._win32gui.GetWindowText(hwnd).lower():
                self._win32gui.ShowWindow(hwnd, 9)  # SW_RESTORE
                try:
                    self._win32gui.SetForegroundWindow(hwnd)
                except Exception:
                    pass
                _cb.found = True
                return False  # stop enumeration
            return True

        _cb.found = False
        self._win32gui.EnumWindows(_cb, None)
        if getattr(_cb, "found", False):
            return {"success": True, "window": title}
        return {"success": False, "error": f"No visible window matched '{title}'"}

    # ──────────────── Cross-platform launch ───────────────────────────────────

    def open_app(self, app: str) -> dict:
        """Open an app by name/path. Uses `start` on Windows, `open` on macOS, else search PATH."""
        if _IS_WINDOWS:
            resolved = shutil.which(app)
            if resolved:
                try:
                    os.startfile(resolved)  # type: ignore[attr-defined]
                    return {"success": True, "app": app, "method": "os.startfile"}
                except Exception:
                    pass
            try:
                os.startfile(app)  # type: ignore[attr-defined]
                return {"success": True, "app": app, "method": "os.startfile"}
            except Exception:
                pass
            try:
                subprocess.Popen(["start", "", app], shell=True)
                return {"success": True, "app": app, "method": "start"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        if platform.system() == "Darwin":
            subprocess.Popen(["open", "-a", app])
            return {"success": True, "app": app, "method": "open -a"}
        resolved = shutil.which(app)
        if resolved:
            subprocess.Popen([resolved])
            return {"success": True, "app": app, "method": "PATH"}
        return {"success": False, "error": f"Could not launch '{app}'"}

    # ──────────────── Mouse & keyboard (pyautogui) ───────────────────────────

    def click(self, x: int, y: int, button: str = "left", clicks: int = 1) -> dict:
        if self._pyautogui is None:
            return {"success": False, "error": "pyautogui not installed — cannot click"}
        self._pyautogui.click(x, y, clicks=clicks, button=button)
        return {"success": True, "x": x, "y": y, "button": button}

    def type_text(self, text: str, interval: float = 0.0) -> dict:
        if self._pyautogui is None:
            return {"success": False, "error": "pyautogui not installed — cannot type"}
        self._pyautogui.typewrite(text, interval=interval)
        return {"success": True, "chars": len(text)}

    def press_key(self, key: str) -> dict:
        if self._pyautogui is None:
            return {"success": False, "error": "pyautogui not installed — cannot press keys"}
        self._pyautogui.press(key)
        return {"success": True, "key": key}

    def get_cursor(self) -> dict:
        if self._pyautogui is None:
            return {"success": False, "error": "pyautogui not installed"}
        x, y = self._pyautogui.position()
        return {"success": True, "x": x, "y": y}

    # ──────────────── Screen ──────────────────────────────────────────────────

    def screen_size(self) -> dict:
        if self._pyautogui is None:
            return {"success": False, "error": "pyautogui not installed"}
        w, h = self._pyautogui.size()
        return {"success": True, "width": w, "height": h}

    # ──────────────── Desktop summary (drives the autopilot "organize" goal) ──

    def desktop_summary(self) -> dict:
        """Snapshot of the current desktop: status, open windows, screen size.
        Used to seed the autopilot planner when a desktop-organization goal is set."""
        summary = {"available": self.available}
        windows = self.list_windows()
        summary.update(windows)
        summary["size"] = self.screen_size()
        return summary


_engine: ComputerControl | None = None


def get_computer_control() -> ComputerControl:
    global _engine
    if _engine is None:
        _engine = ComputerControl()
    return _engine

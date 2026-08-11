"""Global hotkey — summon/focus Friday from anywhere (P2).

Registers a system-wide hotkey (default Ctrl+Alt+F) using the optional
``keyboard`` library and, when pressed, opens the frontend URL in the default
browser. Fully optional: if ``keyboard`` is not installed the module degrades
to no-op so the API server still boots.
"""

import threading
import webbrowser

from core.logger import info

DEFAULT_HOTKEY = "ctrl+alt+f"
FRONTEND_URL = "http://localhost:5173"

_enabled = False
_thread: threading.Thread | None = None


def start_hotkey_listener(hotkey: str = DEFAULT_HOTKEY, url: str = FRONTEND_URL) -> bool:
    """Start the global hotkey listener in a daemon thread. Returns True if active."""
    global _enabled, _thread
    if _enabled:
        return True
    try:
        import keyboard  # type: ignore
    except ImportError:
        info("Global hotkey disabled — install 'keyboard' (pip install keyboard) to summon Friday anywhere")
        return False

    def _handler():
        webbrowser.open(url)

    def _loop():
        try:
            keyboard.add_hotkey(hotkey, _handler)
            info(f"Global hotkey active: {hotkey} → {url}")
            keyboard.wait()
        except Exception as e:  # noqa: BLE001
            info(f"Global hotkey listener stopped: {e}")

    _thread = threading.Thread(target=_loop, daemon=True, name="friday-hotkey")
    _thread.start()
    _enabled = True
    return True


def stop_hotkey_listener():
    global _enabled
    if _enabled:
        try:
            import keyboard  # type: ignore

            keyboard.unhook_all_hotkeys()
        except Exception:  # noqa: BLE001
            pass
        _enabled = False

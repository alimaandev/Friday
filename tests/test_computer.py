from core.computer import ComputerControl
from core.security import get_permission_manager


def test_available_reports_capabilities():
    cc = ComputerControl()
    info = cc.available
    assert "platform" in info
    assert "mouse_keyboard" in info
    assert "window_management" in info


def test_open_app_missing_binary_returns_error():
    cc = ComputerControl()
    result = cc.open_app("__definitely_not_a_real_app_xyz__")
    assert "success" in result


def test_type_text_without_pyautogui_is_graceful(monkeypatch):
    cc = ComputerControl()
    monkeypatch.setattr(cc, "_pyautogui", None)
    result = cc.type_text("hello")
    assert result["success"] is False
    assert "error" in result


def test_click_without_pyautogui_is_graceful(monkeypatch):
    cc = ComputerControl()
    monkeypatch.setattr(cc, "_pyautogui", None)
    result = cc.click(10, 20)
    assert result["success"] is False


def test_list_windows_without_win32_is_graceful(monkeypatch):
    cc = ComputerControl()
    monkeypatch.setattr(cc, "_win32gui", None)
    result = cc.list_windows()
    assert "windows" in result


def test_close_app_without_win32_is_graceful(monkeypatch):
    cc = ComputerControl()
    monkeypatch.setattr(cc, "_win32gui", None)
    result = cc.close_app("notepad")
    assert result["success"] is False


def test_desktop_summary_merges_state(monkeypatch):
    cc = ComputerControl()
    monkeypatch.setattr(cc, "_win32gui", None)
    monkeypatch.setattr(cc, "_pyautogui", None)
    summary = cc.desktop_summary()
    assert "available" in summary
    assert "windows" in summary
    assert "size" in summary


def test_control_tools_require_confirmation():
    perm = get_permission_manager()
    for tool in ("open_app", "type_text", "click_mouse", "press_key", "focus_window", "close_app"):
        result = perm.check_tool(tool, {"app": "notepad", "text": "hi", "x": 1, "y": 1, "key": "enter", "title": "x"})
        assert result.get("requires_confirmation") is True, tool

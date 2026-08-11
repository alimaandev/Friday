from core import hotkey


def test_start_degrades_when_keyboard_missing(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "keyboard":
            raise ImportError("no keyboard")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    assert hotkey.start_hotkey_listener() is False


def test_start_registers_hotkey(monkeypatch):
    calls = {"hotkey": None, "url": None, "wait": 0, "add": 0}

    class FakeKeyboard:
        @staticmethod
        def add_hotkey(hk, cb):
            calls["add"] += 1
            calls["hotkey"] = hk

        @staticmethod
        def wait():
            calls["wait"] += 1

    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "keyboard":
            return FakeKeyboard
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    monkeypatch.setattr(hotkey, "_enabled", False)

    opened = []
    monkeypatch.setattr(hotkey.webbrowser, "open", lambda url: opened.append(url))

    assert hotkey.start_hotkey_listener() is True
    assert calls["add"] == 1
    assert calls["hotkey"] == "ctrl+alt+f"

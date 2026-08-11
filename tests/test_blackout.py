import pytest

from core import blackout


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    store = tmp_path / "blackout.json"
    store.write_text('{"enabled": false}', encoding="utf-8")
    monkeypatch.setattr(blackout, "_STORE_PATH", str(store))
    monkeypatch.setattr(blackout, "_enabled", False)
    yield
    monkeypatch.setattr(blackout, "_enabled", None)


def test_default_off():
    assert blackout.is_blackout() is False


def test_toggle_and_persist(tmp_path):
    blackout.set_blackout(True)
    assert blackout.is_blackout() is True
    state = (tmp_path / "blackout.json").read_text(encoding="utf-8")
    assert '"enabled": true' in state


def test_toggle_off():
    blackout.set_blackout(True)
    blackout.set_blackout(False)
    assert blackout.is_blackout() is False


def test_blocks_network_tools():
    blackout.set_blackout(False)
    assert blackout.is_tool_blocked("web_fetch") is False
    blackout.set_blackout(True)
    assert blackout.is_tool_blocked("web_fetch") is True
    assert blackout.is_tool_blocked("browse_search") is True
    assert blackout.is_tool_blocked("read_file") is False
    assert blackout.is_tool_blocked("write_file") is False


def test_resolve_provider_forces_local():
    blackout.set_blackout(True)
    assert blackout.resolve_provider("openrouter") == "ollama"
    blackout.set_blackout(False)
    assert blackout.resolve_provider("openrouter") == "openrouter"


def test_status_shape():
    blackout.set_blackout(True)
    status = blackout.get_blackout_status()
    assert status["enabled"] is True
    assert status["local_provider"] == "ollama"
    assert "web_fetch" in status["blocked_tools"]

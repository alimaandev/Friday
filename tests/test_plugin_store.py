import json

import pytest

from core.plugin_store import install_plugin, list_marketplace, uninstall_plugin


@pytest.fixture(autouse=True)
def _clean_manifest(tmp_path, monkeypatch):
    import core.plugin_store as ps

    manifest = tmp_path / "manifest.json"
    manifest.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(ps, "_MANIFEST_PATH", str(manifest))
    yield
    manifest.write_text("[]", encoding="utf-8")


def test_install_adds_to_manifest(tmp_path):

    result = install_plugin("fun")
    assert result["success"]
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert any(e["name"] == "fun" for e in manifest)


def test_uninstall_removes_from_manifest(tmp_path):
    install_plugin("fun")
    result = uninstall_plugin("fun")
    assert result["success"]
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert all(e["name"] != "fun" for e in manifest)


def test_install_missing_plugin_fails():
    result = install_plugin("__does_not_exist__")
    assert result["success"] is False


def test_list_marketplace_reports_builtins_and_community():
    plugins = list_marketplace()
    names = {p["name"] for p in plugins}
    assert "run_command" in names or "open_app" in names
    assert "fun" in names

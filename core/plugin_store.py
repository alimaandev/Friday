"""Plugin marketplace — manifest registry for installable/removable tool plugins.

Built-ins ship with the app and are always present. Third-party plugins can be
added from a local ``plugins/community/`` directory (a simple folder-of-modules
marketplace). The registry keeps a JSON manifest of installed community plugins
so installs/removals persist across restarts.

This mirrors the v4-plan's "manifest registry, install/remove UI in settings".
"""

import json
import os
import shutil

from core.logger import info

_APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PLUGINS_DIR = os.path.join(_APP_DIR, "plugins")
_COMMUNITY_DIR = os.path.join(_PLUGINS_DIR, "community")
_MANIFEST_PATH = os.path.join(_PLUGINS_DIR, "manifest.json")

MANIFEST_KEYS = {"name", "description", "version", "author", "tools"}


def _ensure_dirs():
    os.makedirs(_COMMUNITY_DIR, exist_ok=True)


def _load_manifest() -> list[dict]:
    if not os.path.exists(_MANIFEST_PATH):
        return []
    try:
        with open(_MANIFEST_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_manifest(entries: list[dict]):
    _ensure_dirs()
    with open(_MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


def _entry_candidates() -> list[dict]:
    """Discover every module folder under plugins/community/ as a candidate."""
    if not os.path.isdir(_COMMUNITY_DIR):
        return []
    entries = []
    for name in sorted(os.listdir(_COMMUNITY_DIR)):
        candidate = os.path.join(_COMMUNITY_DIR, name)
        if os.path.isdir(candidate) and os.path.isfile(os.path.join(candidate, "__init__.py")):
            entries.append({"name": name, "path": name})
    return entries


def list_marketplace() -> list[dict]:
    """Return built-in + community plugin entries for the Settings UI."""
    _ensure_dirs()
    installed_names = {e.get("name") for e in _load_manifest()}
    plugins: list[dict] = []

    from core import registry

    for pname in registry.list_plugins():
        plugins.append(
            {
                "name": pname,
                "builtin": True,
                "installed": True,
                "enabled": True,
                "description": "",
            }
        )

    for candidate in _entry_candidates():
        plugins.append(
            {
                "name": candidate["name"],
                "builtin": False,
                "installed": candidate["name"] in installed_names,
                "enabled": candidate["name"] in installed_names,
                "description": "Community tool plugin.",
            }
        )

    return plugins


def install_plugin(name: str) -> dict:
    """Install a community plugin folder into the manifest (whitelist)."""
    _ensure_dirs()
    target = os.path.join(_COMMUNITY_DIR, name)
    if not os.path.isdir(target):
        return {"success": False, "error": f"Plugin '{name}' not found in plugins/community/"}

    manifest = _load_manifest()
    if any(e.get("name") == name for e in manifest):
        return {"success": True, "message": "already installed"}

    manifest.append({"name": name, "version": "0.1", "author": "community", "tools": []})
    _save_manifest(manifest)
    try:
        reload_plugins()
    except Exception as e:  # noqa: BLE001
        info(f"Plugin install post-reload skipped: {e}")
    return {"success": True, "message": f"installed {name}"}


def uninstall_plugin(name: str) -> dict:
    _ensure_dirs()
    manifest = _load_manifest()
    filtered = [e for e in manifest if e.get("name") != name]
    if len(filtered) == len(manifest):
        return {"success": False, "error": f"Plugin '{name}' is not installed"}
    _save_manifest(filtered)
    try:
        reload_plugins()
    except Exception as e:  # noqa: BLE001
        info(f"Plugin uninstall post-reload skipped: {e}")
    return {"success": True, "message": f"uninstalled {name}"}


def reload_plugins():
    """Re-discover tools so newly installed community plugins take effect."""
    from core import registry

    installed_names = {e.get("name") for e in _load_manifest()}

    for entry in _entry_candidates():
        if entry["name"] in installed_names:
            try:
                import importlib

                importlib.import_module("plugins.community." + entry["name"])
            except Exception as e:  # noqa: BLE001
                info(f"Could not load community plugin {entry['name']}: {e}")

    registry.discover_plugins()
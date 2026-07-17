import importlib
import inspect
import pkgutil
from typing import Any

from plugins.base import ToolPlugin
from core.logger import info, warn

_TOOL_DEFINITIONS: list[dict[str, Any]] = []
_TOOL_MAP: dict[str, Any] = {}
_PLUGIN_INSTANCES: dict[str, ToolPlugin] = {}


_EXCLUDED_TOOLS = {
    "close_browser",
    "is_voice_available",
    "browse_",  # prefix for internal browser helpers
}

def _is_tool_allowed(name: str) -> bool:
    if name in _EXCLUDED_TOOLS:
        return False
    if name.startswith("_"):
        return False
    return True


def discover_plugins():
    _TOOL_DEFINITIONS.clear()
    _TOOL_MAP.clear()
    _PLUGIN_INSTANCES.clear()

    _scan_package("plugins.builtins")
    _scan_tools_fallback()

    info(f"Tool discovery complete: {len(_TOOL_MAP)} tools, {len(_TOOL_DEFINITIONS)} definitions")


def _scan_package(package_name: str):
    try:
        pkg = importlib.import_module(package_name)
        path = getattr(pkg, "__path__", None)
        if not path:
            return
        for importer, modname, is_pkg in pkgutil.walk_packages(path, f"{package_name}."):
            if is_pkg:
                continue
            try:
                mod = importlib.import_module(modname)
                _register_plugins_from_module(mod)
            except Exception as e:
                warn(f"Failed to load plugin {modname}: {e}")
    except ImportError:
        pass


def _scan_tools_fallback():
    from tools import python_repl, search, shell, voice
    for mod in (python_repl, search, shell, voice):
        _register_functions_from_module(mod)


def _register_plugins_from_module(module):
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if (
            issubclass(obj, ToolPlugin)
            and obj is not ToolPlugin
            and hasattr(obj, "name")
            and obj.name
        ):
            try:
                instance = obj()
                name = instance.name
                if name in _TOOL_MAP:
                    warn(f"Plugin '{name}' already registered, skipping duplicate")
                    continue
                _PLUGIN_INSTANCES[name] = instance
                _TOOL_DEFINITIONS.append(instance.get_tool_definition())
                _TOOL_MAP[name] = instance.execute
                info(f"Registered plugin tool: {name}")
            except Exception as e:
                warn(f"Failed to instantiate plugin {name}: {e}")


def _register_functions_from_module(module):
    for name, obj in inspect.getmembers(module, inspect.isfunction):
        if getattr(obj, "__module__", "") != module.__name__:
            continue
        if not _is_tool_allowed(name):
            continue
        if name in _TOOL_MAP:
            continue
        _TOOL_MAP[name] = obj
        try:
            sig = inspect.signature(obj)
            properties = {}
            required = []
            for pname, param in sig.parameters.items():
                if pname in ("self", "cls", "args", "kwargs"):
                    continue
                prop = {"type": "string", "description": pname}
                if param.default is inspect.Parameter.empty:
                    required.append(pname)
                if param.annotation is not inspect.Parameter.empty:
                    ann = param.annotation
                    if ann is int:
                        prop["type"] = "integer"
                    elif ann is float:
                        prop["type"] = "number"
                    elif ann is bool:
                        prop["type"] = "boolean"
                    elif ann is list:
                        prop["type"] = "array"
                properties[pname] = prop
            _TOOL_DEFINITIONS.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": (obj.__doc__ or f"Execute {name}").strip()[:200],
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required,
                    },
                },
            })
        except Exception as e:
            warn(f"Could not generate definition for {name}: {e}")


def register_tool(name: str, func: callable, definition: dict | None = None):
    _TOOL_MAP[name] = func
    if definition:
        _TOOL_DEFINITIONS.append(definition)
    info(f"Registered legacy tool: {name}")


def get_tool_definitions() -> list[dict[str, Any]]:
    return _TOOL_DEFINITIONS


def get_tool_map() -> dict[str, Any]:
    return _TOOL_MAP


def get_plugin(name: str) -> ToolPlugin | None:
    return _PLUGIN_INSTANCES.get(name)


def list_plugins() -> list[str]:
    return list(_PLUGIN_INSTANCES.keys())


def run_health_checks() -> dict[str, bool]:
    results = {}
    for name in _TOOL_MAP:
        results[name] = True
    return results

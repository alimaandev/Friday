"""Custom tool builder — natural language → persisted tool definitions.

Users describe a tool in plain language; the LLM generates a name,
description, parameter schema, and a Python body. Tools are persisted to
``memory_store/custom_tools.json`` and registered into the tool registry so
they behave exactly like built-in plugins.
"""

import json
import os
import re

from core.logger import info

_APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_STORE_PATH = os.path.join(os.path.join(_APP_DIR, "memory_store"), "custom_tools.json")

_BUILD_PROMPT = """You are the Friday tool builder. Turn the user's request into ONE tool definition.

Return ONLY a JSON object with these fields:
- "name": snake_case, max 40 chars, no spaces
- "description": 1-2 sentences describing what the tool does, for the LLM's tool list
- "parameters": JSON Schema for an object parameter (properties + required + type:"object")
- "body": a Python function body that defines `def run(**kwargs) -> dict`. It receives the
  validated parameters as kwargs and must return a dict. Import any stdlib at the top of the body.
  Do NOT print. Keep it simple and safe; never delete user files unless asked.

Example:
{"name": "list_sizes", "description": "Return the byte size of files in a directory.",
 "parameters": {"type":"object","properties":{"dir":{"type":"string","description":"directory path"}},"required":["dir"]},
 "body": "import os\\ndef run(**kwargs):\\n    d = kwargs.get('dir', '.')\\n    return {'sizes': [{'f': f, 'bytes': os.path.getsize(os.path.join(d, f))} for f in os.listdir(d)]}"}
"""


def _load() -> list[dict]:
    if not os.path.exists(_STORE_PATH):
        return []
    try:
        with open(_STORE_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save(tools: list[dict]):
    os.makedirs(os.path.dirname(_STORE_PATH), exist_ok=True)
    with open(_STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(tools, f, indent=2, ensure_ascii=False)


def list_custom_tools() -> list[dict]:
    return _load()


def get_custom_tool(name: str) -> dict | None:
    for tool in _load():
        if tool.get("name") == name:
            return tool
    return None


def register_custom_tools():
    """Inject persisted custom tools into the tool registry."""
    from core import registry

    for tool in _load():
        name = tool.get("name")
        if not name:
            continue
        body = tool.get("body", "")
        if name in registry.get_tool_map():
            continue
        handler = _make_handler(body, name)
        definition = {
            "type": "function",
            "function": {
                "name": name,
                "description": tool.get("description", ""),
                "parameters": tool.get("parameters", {"type": "object", "properties": {}, "required": []}),
            },
        }
        registry.register_tool(name, handler, definition)
        info(f"Registered custom tool: {name}")


def _make_handler(body: str, name: str):
    def handler(**kwargs) -> dict:
        ns: dict = {}
        try:
            exec(compile(body, f"<custom:{name}>", "exec"), ns)
        except Exception as e:  # noqa: BLE001
            return {"error": f"Compile error in custom tool '{name}': {e}"}
        fn = ns.get("run")
        if not callable(fn):
            return {"error": f"Custom tool '{name}' has no run(**kwargs)"}
        try:
            return fn(**kwargs) or {"success": True}
        except Exception as e:  # noqa: BLE001
            return {"error": f"Custom tool '{name}' failed: {e}"}

    return handler


def _extract_json(raw: str) -> dict:
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError("No JSON object in LLM response")
    return json.loads(match.group(0))


def build_tool_from_nl(description: str, llm_chat=None) -> dict:
    """Ask the LLM to design a tool from a natural-language description."""
    from agent.llm import chat as default_chat

    chat = llm_chat or default_chat
    messages = [
        {"role": "system", "content": _BUILD_PROMPT},
        {"role": "user", "content": description},
    ]
    raw = ""
    for event in chat(messages):
        if event.get("type") == "tokens":
            raw += event.get("content", "")
        elif event.get("type") == "done":
            raw = event.get("content", raw)

    spec = _extract_json(raw)
    spec["description_source"] = description
    return spec


def create_custom_tool(description: str, llm_chat=None) -> dict:
    """Validate a NL-built tool and persist it."""
    spec = build_tool_from_nl(description, llm_chat=llm_chat)
    name = (spec.get("name") or "").strip().lower()
    if not re.fullmatch(r"[a-z_][a-z0-9_]{0,39}", name):
        raise ValueError(f"Invalid tool name: {name!r}")
    if not spec.get("body") or "def run" not in spec.get("body", ""):
        raise ValueError("Generated tool body is missing a run() function")

    tools = _load()
    if any(t.get("name") == name for t in tools):
        raise ValueError(f"Custom tool '{name}' already exists")

    tool = {
        "name": name,
        "description": spec.get("description", ""),
        "parameters": spec.get("parameters", {"type": "object", "properties": {}, "required": []}),
        "body": spec["body"],
        "source": spec.get("description_source", description),
    }
    tools.append(tool)
    _save(tools)
    register_custom_tools()
    return tool


def delete_custom_tool(name: str) -> bool:
    tools = _load()
    filtered = [t for t in tools if t.get("name") != name]
    if len(filtered) == len(tools):
        return False
    _save(filtered)
    from core import registry

    registry.get_tool_map().pop(name, None)
    registry.get_tool_definitions()[:] = [
        d for d in registry.get_tool_definitions() if not (d.get("function", {}).get("name") == name)
    ]
    return True

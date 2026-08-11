import json

import pytest

from core.custom_tools import (
    _extract_json,
    _make_handler,
    build_tool_from_nl,
    create_custom_tool,
    delete_custom_tool,
    get_custom_tool,
    list_custom_tools,
)


@pytest.fixture(autouse=True)
def _clean_store(tmp_path, monkeypatch):
    import core.custom_tools as ct

    store = tmp_path / "custom_tools.json"
    store.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(ct, "_STORE_PATH", str(store))
    yield
    store.write_text("[]", encoding="utf-8")


def test_extract_json_handles_markdown_fence():
    raw = '```json\n{"name": "x", "description": "y"}\n```'
    assert _extract_json(raw) == {"name": "x", "description": "y"}


def test_make_handler_runs_body():
    body = "def run(**kwargs):\n    a = kwargs.get('a', 0)\n    b = kwargs.get('b', 0)\n    return {'sum': a + b}"
    handler = _make_handler(body, "add")
    result = handler(a=2, b=3)
    assert result == {"sum": 5}


def test_make_handler_reports_compile_error():
    handler = _make_handler("this is not python !!!", "bad")
    result = handler()
    assert "error" in result


def test_make_handler_reports_missing_run():
    handler = _make_handler("x = 1", "norun")
    result = handler()
    assert "error" in result


def test_create_custom_tool_persists(tmp_path):
    def fake_chat(messages, tools=None):
        yield {
            "type": "done",
            "content": json.dumps(
                {
                    "name": "dir_size",
                    "description": "Returns size of a directory",
                    "parameters": {
                        "type": "object",
                        "properties": {"path": {"type": "string", "description": "dir path"}},
                        "required": ["path"],
                    },
                    "body": "import os\ndef run(**kwargs):\n    return {'ok': True}",
                }
            ),
        }

    tool = create_custom_tool("size of a folder", llm_chat=fake_chat)
    assert tool["name"] == "dir_size"
    assert get_custom_tool("dir_size") is not None


def test_create_duplicate_rejected(tmp_path):
    def fake_chat(messages, tools=None):
        yield {
            "type": "done",
            "content": json.dumps(
                {
                    "name": "dup_tool",
                    "description": "d",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "body": "def run(**kwargs):\n    return {}",
                }
            ),
        }

    create_custom_tool("first", llm_chat=fake_chat)
    with pytest.raises(ValueError):
        create_custom_tool("second", llm_chat=fake_chat)


def test_invalid_name_rejected(tmp_path):
    def fake_chat(messages, tools=None):
        yield {
            "type": "done",
            "content": json.dumps(
                {
                    "name": "Bad Name!",
                    "description": "d",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "body": "def run(**kwargs):\n    return {}",
                }
            ),
        }

    with pytest.raises(ValueError):
        create_custom_tool("anything", llm_chat=fake_chat)


def test_delete_custom_tool(tmp_path):
    def fake_chat(messages, tools=None):
        yield {
            "type": "done",
            "content": json.dumps(
                {
                    "name": "gone_tool",
                    "description": "d",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "body": "def run(**kwargs):\n    return {}",
                }
            ),
        }

    create_custom_tool("create", llm_chat=fake_chat)
    assert delete_custom_tool("gone_tool") is True
    assert delete_custom_tool("gone_tool") is False
    assert list_custom_tools() == []


def test_build_tool_from_nl_uses_llm():
    def fake_chat(messages, tools=None):
        assert any("tool builder" in m.get("content", "") for m in messages)
        yield {"type": "tokens", "content": '{"name": "t","descr'}
        yield {"type": "done", "content": '{"name": "t", "description": "d"}', "tool_calls": None}

    spec = build_tool_from_nl("build a thing", llm_chat=fake_chat)
    assert spec["name"] == "t"
    assert spec["description_source"] == "build a thing"

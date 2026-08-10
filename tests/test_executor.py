import json

from core.executor import Executor
from core.planner import Task
from core.security import get_approval_registry, get_permission_manager


def _make_llm(*event_lists):
    """Create a mock LLM provider that returns events from each call sequentially."""
    call_count = 0

    def llm(*args, **kwargs):
        nonlocal call_count
        idx = min(call_count, len(event_lists) - 1)
        call_count += 1
        return iter(event_lists[idx])

    return llm


def test_execute_task_no_tool_calls():
    task = Task(id="t1", description="test", tool="none")
    tool_map = {}

    llm = _make_llm(
        [
            {"type": "tokens", "content": "Hello"},
            {"type": "done", "content": "Hello world", "tool_calls": None},
        ]
    )
    ex = Executor(llm, tool_map)
    results = list(ex.execute_task(task, [], [], max_iterations=5))

    assert len(results) >= 2
    assert any(r.get("type") == "tokens" for r in results)
    done = [r for r in results if r.get("type") == "done"][-1]
    assert done["content"] == "Hello world"
    assert task.status == "completed"
    assert task.result == "Hello world"


def test_execute_task_with_tool_call():
    task = Task(id="t2", description="test tool")
    tool_map = {
        "greet": lambda name: {"result": f"Hello, {name}!"},
    }

    llm = _make_llm(
        # First call: returns a tool call
        [
            {"type": "tokens", "content": "Let me greet"},
            {
                "type": "done",
                "content": "Let me greet",
                "tool_calls": [
                    {"id": "call_1", "function": {"name": "greet", "arguments": json.dumps({"name": "World"})}},
                ],
            },
        ],
        # Second call: returns final response
        [
            {"type": "tokens", "content": "Done"},
            {"type": "done", "content": "Done greeting", "tool_calls": None},
        ],
    )
    ex = Executor(llm, tool_map)
    results = list(ex.execute_task(task, [], [], max_iterations=5))

    tool_results = [r for r in results if r["type"] == "tool_result"]
    assert len(tool_results) == 1
    assert tool_results[0]["tools"][0]["name"] == "greet"

    done_events = [r for r in results if r["type"] == "done"]
    assert done_events[-1]["content"] == "Done greeting"


def test_execute_task_unknown_tool():
    task = Task(id="t3", description="unknown tool")
    tool_map = {}

    llm = _make_llm(
        [
            {
                "type": "done",
                "content": "Calling tool",
                "tool_calls": [
                    {"id": "call_2", "function": {"name": "nonexistent", "arguments": "{}"}},
                ],
            }
        ],
        [{"type": "done", "content": "Final", "tool_calls": None}],
    )
    ex = Executor(llm, tool_map)
    results = list(ex.execute_task(task, [], [], max_iterations=5))
    tool_result = [r for r in results if r["type"] == "tool_result"][0]
    assert "Unknown tool" in tool_result["tools"][0]["result"]


def test_execute_task_tool_error():
    task = Task(id="t4", description="tool error")

    def failing_tool(**kwargs):
        raise ValueError("Something broke")

    tool_map = {"fail": failing_tool}
    llm = _make_llm(
        [
            {
                "type": "done",
                "content": "Calling fail",
                "tool_calls": [
                    {"id": "c3", "function": {"name": "fail", "arguments": "{}"}},
                ],
            }
        ],
        [{"type": "done", "content": "Final", "tool_calls": None}],
    )
    ex = Executor(llm, tool_map)
    list(ex.execute_task(task, [], [], max_iterations=5))
    assert task.error is not None


def test_execute_task_invalid_args():
    task = Task(id="t5", description="invalid args")
    tool_map = {"echo": lambda **k: {"result": k}}
    llm = _make_llm(
        [
            {
                "type": "done",
                "content": "",
                "tool_calls": [
                    {"id": "c4", "function": {"name": "echo", "arguments": "not-json"}},
                ],
            }
        ],
        [{"type": "done", "content": "Final", "tool_calls": None}],
    )
    ex = Executor(llm, tool_map)
    results = list(ex.execute_task(task, [], [], max_iterations=5))
    assert any(r.get("type") == "tool_result" for r in results)
    assert task.status == "completed"
    assert task.result == "Final"


def test_execute_task_max_iterations():
    """Should stop after max_iterations when LLM keeps making tool calls."""
    task = Task(id="t6", description="infinite loop")
    tool_map = {"ping": lambda: {"result": "pong"}}

    # Always returns a tool call — will hit max iterations
    llm = _make_llm(
        [
            {
                "type": "done",
                "content": "",
                "tool_calls": [
                    {"id": "cx", "function": {"name": "ping", "arguments": "{}"}},
                ],
            }
        ]
    )
    ex = Executor(llm, tool_map)
    results = list(ex.execute_task(task, [], [], max_iterations=3))
    done_events = [r for r in results if r["type"] == "done"]
    assert "Max iterations" in done_events[-1]["content"]
    assert task.status == "failed"
    assert task.error == "Max iterations reached"


def test_retry_task():
    task = Task(id="t7", description="retry me", error="First attempt failed", retries=1, max_retries=3)
    tool_map = {"ping": lambda: {"result": "pong"}}

    llm = _make_llm(
        [{"type": "tokens", "content": "Retrying"}, {"type": "done", "content": "OK", "tool_calls": None}],
    )
    ex = Executor(llm, tool_map)
    list(ex.retry_task(task, [], []))
    assert task.status == "completed"


def test_retry_task_max_retries_exceeded():
    task = Task(id="t8", description="exhausted", retries=3, max_retries=3)
    ex = Executor(lambda *a, **kw: iter([]), {})
    results = list(ex.retry_task(task, [], []))
    assert "Max retries" in results[0]["tools"][0]["result"]


def test_output_dir_rewrites_path():
    task = Task(id="t9", description="write file")
    tool_map = {"write_file": lambda path, content: {"result": f"Wrote to {path}"}}

    llm = _make_llm(
        [
            {
                "type": "done",
                "content": "",
                "tool_calls": [
                    {
                        "id": "cw",
                        "function": {
                            "name": "write_file",
                            "arguments": json.dumps({"path": "output.txt", "content": "data"}),
                        },
                    },
                ],
            }
        ],
        [{"type": "done", "content": "Done", "tool_calls": None}],
    )
    ex = Executor(llm, tool_map)
    ex.output_dir = "/custom/output"
    results = list(ex.execute_task(task, [], [], max_iterations=5))
    tool_result = [r for r in results if r["type"] == "tool_result"][0]
    result = tool_result["tools"][0]["result"]
    assert "/custom/output" in result or "\\custom\\output" in result
    assert "output.txt" in result


def test_react_loop_catches_exception():
    task = Task(id="t10", description="crash")
    ex = Executor(None, {})

    def broken_impl(*args, **kwargs):
        raise RuntimeError("Boom!")

    ex._react_loop_impl = broken_impl
    results = list(ex._react_loop([], [], 5, task))
    assert results[0]["type"] == "done"
    assert "Boom!" in results[0]["content"]
    assert task.status == "failed"


def test_execute_task_confirmation_denied():
    task = Task(id="t11", description="destructive")
    tool_map = {"delete_file": lambda path: {"result": "deleted"}}

    llm = _make_llm(
        [
            {
                "type": "done",
                "content": "",
                "tool_calls": [
                    {
                        "id": "cd",
                        "function": {
                            "name": "delete_file",
                            "arguments": json.dumps({"path": "rm -rf project"}),
                        },
                    }
                ],
            }
        ],
        [{"type": "done", "content": "Final", "tool_calls": None}],
    )
    # Enable interactive mode so destructive tools require confirmation
    get_permission_manager().set_interactive(True)
    ex = Executor(llm, tool_map)

    results = []
    gen = ex.execute_task(task, [], [], max_iterations=5)
    for event in gen:
        results.append(event)
        if event["type"] == "requires_confirmation":
            get_approval_registry().resolve(event["request_id"], False)

    confirm_events = [r for r in results if r["type"] == "requires_confirmation"]
    assert len(confirm_events) == 1
    assert confirm_events[0]["tool"] == "delete_file"
    tool_result = [r for r in results if r["type"] == "tool_result"][0]
    assert "cancelled by user" in tool_result["tools"][0]["result"]


def test_execute_task_confirmation_approved():
    task = Task(id="t11", description="destructive approved")
    tool_map = {"delete_file": lambda path: {"result": f"deleted {path}"}}

    llm = _make_llm(
        [
            {
                "type": "done",
                "content": "",
                "tool_calls": [
                    {
                        "id": "ca",
                        "function": {
                            "name": "delete_file",
                            "arguments": json.dumps({"path": "rm -rf backup"}),
                        },
                    }
                ],
            }
        ],
        [{"type": "done", "content": "Final", "tool_calls": None}],
    )

    get_permission_manager().set_interactive(True)
    ex = Executor(llm, tool_map)

    results = []
    gen = ex.execute_task(task, [], [], max_iterations=5)
    for event in gen:
        results.append(event)
        if event["type"] == "requires_confirmation":
            get_approval_registry().resolve(event["request_id"], True)

    confirm_events = [r for r in results if r["type"] == "requires_confirmation"]
    assert len(confirm_events) == 1
    tool_result = [r for r in results if r["type"] == "tool_result"][0]
    assert "deleted rm -rf backup" in tool_result["tools"][0]["result"]
    assert task.status == "completed"


def test_execute_task_denied_tool_blocked():
    task = Task(id="t12", description="denied tool")
    tool_map = {"delete_file": lambda path: {"result": "deleted"}}

    llm = _make_llm(
        [
            {
                "type": "done",
                "content": "",
                "tool_calls": [
                    {"id": "cn", "function": {"name": "delete_file", "arguments": json.dumps({"path": "x"})}},
                ],
            }
        ],
        [{"type": "done", "content": "Final", "tool_calls": None}],
    )

    get_permission_manager().deny_tool("delete_file")
    ex = Executor(llm, tool_map)
    results = list(ex.execute_task(task, [], [], max_iterations=5))

    confirm_events = [r for r in results if r["type"] == "requires_confirmation"]
    assert len(confirm_events) == 0
    tool_result = [r for r in results if r["type"] == "tool_result"][0]
    assert "Blocked by security policy" in tool_result["tools"][0]["result"]

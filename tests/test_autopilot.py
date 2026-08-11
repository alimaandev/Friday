import json

from core.autopilot import Autopilot
from core.planner import Task


class FakePlanner:
    def __init__(self, tasks):
        self.tasks = tasks
        self.created_goals = []

    def create_plan(self, goal, context=None):
        self.created_goals.append(goal)
        return list(self.tasks)


def _make_llm(*event_lists):
    """Mock LLM provider that returns events from each call, sequentially."""
    call_count = 0

    def llm(*args, **kwargs):
        nonlocal call_count
        idx = min(call_count, len(event_lists) - 1)
        call_count += 1
        return iter(event_lists[idx])

    return llm


def _tool_call(tool_id, name, args):
    return {"id": tool_id, "function": {"name": name, "arguments": json.dumps(args)}}


def _run(autopilot, goal="build something"):
    return list(autopilot.run(goal))


def _autopilot_events(results):
    return [e for e in results if e.get("type") == "autopilot"]


def _autopilot_event_names(results):
    return [e["event"] for e in _autopilot_events(results)]


def test_run_emits_orchestration_events():
    planner = FakePlanner([Task(id="t1", description="say hello", tool="none")])
    llm = _make_llm(
        [{"type": "tokens", "content": "Hi"}, {"type": "done", "content": "Hello world", "tool_calls": None}]
    )
    auto = Autopilot(planner, llm, {}, [])

    results = _run(auto)
    names = _autopilot_event_names(results)

    assert names[0] == "plan_started"
    assert names[1] == "plan"
    assert names[2] == "step_start"
    assert names[3] == "step_done"
    assert names[-1] == "done"

    plan_event = _autopilot_events(results)[1]
    assert plan_event["tasks"][0]["id"] == "t1"
    done = results[-1]
    assert done["type"] == "done"
    assert done["final"] is True
    assert "1 completed" in done["content"]

    stats = _autopilot_events(results)[-1]["stats"]
    assert stats == {"total": 1, "completed": 1, "failed": 0, "skipped": 0}


def test_run_passthrough_events_from_executor():
    planner = FakePlanner([Task(id="t1", description="greet", tool="greet")])
    tool_map = {"greet": lambda name: {"result": f"Hello, {name}!"}}
    llm = _make_llm(
        [
            {"type": "tokens", "content": "Let me greet"},
            {
                "type": "done",
                "content": "",
                "tool_calls": [_tool_call("c1", "greet", {"name": "World"})],
            },
        ],
        [{"type": "done", "content": "Greeted", "tool_calls": None}],
    )
    auto = Autopilot(planner, llm, tool_map, [])
    results = _run(auto)

    tool_results = [e for e in results if e["type"] == "tool_result"]
    assert len(tool_results) == 1
    assert "Hello, World!" in tool_results[0]["tools"][0]["result"]


def test_dependency_order_is_topological():
    order_log = []
    tool_map = {"mark": lambda name: order_log.append(name) or {"result": f"marked {name}"}}
    planner = FakePlanner(
        [
            Task(id="b", description="second", tool="mark", args={"name": "b"}, dependencies=["a"]),
            Task(id="a", description="first", tool="mark", args={"name": "a"}),
            Task(id="c", description="third", tool="mark", args={"name": "c"}, dependencies=["b"]),
        ]
    )
    llm = _make_llm(
        [{"type": "done", "content": "", "tool_calls": [_tool_call("c1", "mark", {"name": "a"})]}],
        [{"type": "done", "content": "x", "tool_calls": None}],
        [{"type": "done", "content": "", "tool_calls": [_tool_call("c1", "mark", {"name": "b"})]}],
        [{"type": "done", "content": "y", "tool_calls": None}],
        [{"type": "done", "content": "", "tool_calls": [_tool_call("c1", "mark", {"name": "c"})]}],
        [{"type": "done", "content": "z", "tool_calls": None}],
    )
    auto = Autopilot(planner, llm, tool_map, [])
    results = _run(auto)

    assert order_log == ["a", "b", "c"]
    step_starts = [e for e in _autopilot_events(results) if e["event"] == "step_start"]
    assert [e["task"]["id"] for e in step_starts] == ["a", "b", "c"]


def test_failed_dependency_skips_dependents():
    tool_map = {"fail": lambda: {"error": "boom"}}
    planner = FakePlanner(
        [
            Task(id="a", description="fails", tool="fail"),
            Task(id="b", description="skipped", tool="fail", dependencies=["a"]),
        ]
    )
    llm = _make_llm(
        [{"type": "done", "content": "", "tool_calls": [_tool_call("c1", "fail", {})]}],
        [{"type": "done", "content": "failed", "tool_calls": None}],
        [{"type": "done", "content": "unused", "tool_calls": None}],
    )
    auto = Autopilot(planner, llm, tool_map, [])
    results = _run(auto)

    events = _autopilot_events(results)
    skipped = [e for e in events if e["event"] == "step_skipped"]
    assert len(skipped) == 1
    assert skipped[0]["task"]["id"] == "b"
    stats = [e for e in events if e["event"] == "done"][0]["stats"]
    assert stats["failed"] == 1 and stats["skipped"] == 1


def test_dependency_cycle_fails_remaining_tasks():
    planner = FakePlanner(
        [
            Task(id="a", description="a", tool="none", dependencies=["b"]),
            Task(id="b", description="b", tool="none", dependencies=["a"]),
        ]
    )
    llm = _make_llm([{"type": "done", "content": "ok", "tool_calls": None}])
    auto = Autopilot(planner, llm, {}, [])
    results = _run(auto, goal="cycle")

    names = _autopilot_event_names(results)
    assert "aborted" not in names
    assert planner.tasks[0].status == "failed"
    assert planner.tasks[1].status == "failed"
    assert "cycle" in planner.tasks[0].error
    done_event = [e for e in _autopilot_events(results) if e["event"] == "done"][0]
    assert done_event["stats"]["failed"] == 2


def test_workspace_confines_absolute_paths(tmp_path):
    planner = FakePlanner([Task(id="t1", description="steal", tool="read_file", args={"path": "secret"})])
    tool_map = {"read_file": lambda path: {"result": f"read {path}"}}
    llm = _make_llm(
        [
            {
                "type": "done",
                "content": "",
                "tool_calls": [_tool_call("c1", "read_file", {"path": str(tmp_path.parent)})],
            }
        ],
        [{"type": "done", "content": "conceded", "tool_calls": None}],
    )
    auto = Autopilot(planner, llm, tool_map, [], workspace=str(tmp_path))
    results = _run(auto)

    names = _autopilot_event_names(results)
    assert "aborted" in names
    aborted = [e for e in _autopilot_events(results) if e["event"] == "aborted"][0]
    assert "outside the workspace" in aborted["reason"]

    tool_results = [e for e in results if e["type"] == "tool_result"]
    assert "outside the workspace" in tool_results[0]["tools"][0]["result"]


def test_workspace_roots_relative_write_paths(tmp_path):
    planner = FakePlanner([Task(id="t1", description="write", tool="write_file")])
    written = {}

    def write_file(path, content):
        written["path"] = path
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"result": f"wrote {path}"}

    tool_map = {"write_file": write_file}
    llm = _make_llm(
        [
            {
                "type": "done",
                "content": "",
                "tool_calls": [_tool_call("c1", "write_file", {"path": "out.txt", "content": "hi"})],
            }
        ],
        [{"type": "done", "content": "done", "tool_calls": None}],
    )
    auto = Autopilot(planner, llm, tool_map, [], workspace=str(tmp_path))
    _run(auto)

    assert written["path"] == str(tmp_path / "out.txt")
    assert (tmp_path / "out.txt").exists()


def test_verification_detects_missing_file(tmp_path):
    planner = FakePlanner([Task(id="t1", description="fake write", tool="write_file")])
    tool_map = {"write_file": lambda path, content: {"result": f"claimed {path}"}}
    llm = _make_llm(
        [
            {
                "type": "done",
                "content": "",
                "tool_calls": [_tool_call("c1", "write_file", {"path": "ghost.txt", "content": "x"})],
            },
        ],
        [{"type": "done", "content": "done", "tool_calls": None}],
    )
    auto = Autopilot(planner, llm, tool_map, [], workspace=str(tmp_path))
    results = _run(auto)

    step_done = [e for e in _autopilot_events(results) if e["event"] == "step_done"][0]
    assert step_done["verification"]["verified"] is False
    assert step_done["verification"]["mode"] == "missing_file"


def test_verification_ok_for_existing_file(tmp_path):
    target = tmp_path / "real.txt"
    planner = FakePlanner([Task(id="t1", description="real write", tool="write_file")])

    def write_file(path, content):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"result": f"wrote {path}"}

    tool_map = {"write_file": write_file}
    llm = _make_llm(
        [
            {
                "type": "done",
                "content": "",
                "tool_calls": [_tool_call("c1", "write_file", {"path": "real.txt", "content": "x"})],
            }
        ],
        [{"type": "done", "content": "done", "tool_calls": None}],
    )
    auto = Autopilot(planner, llm, tool_map, [], workspace=str(tmp_path))
    results = _run(auto)

    step_done = [e for e in _autopilot_events(results) if e["event"] == "step_done"][0]
    assert step_done["verification"]["verified"] is True
    assert step_done["verification"]["mode"] == "ok"
    assert target.exists()


def test_verification_detects_tool_error(tmp_path):
    planner = FakePlanner([Task(id="t1", description="boom write", tool="write_file")])
    tool_map = {"write_file": lambda **k: {"error": "disk full"}}
    llm = _make_llm(
        [{"type": "done", "content": "", "tool_calls": [_tool_call("c1", "write_file", {"path": "a.txt"})]}],
        [{"type": "done", "content": "done", "tool_calls": None}],
    )
    auto = Autopilot(planner, llm, tool_map, [], workspace=str(tmp_path))
    results = _run(auto)

    step_done = [e for e in _autopilot_events(results) if e["event"] == "step_done"][0]
    assert step_done["verification"]["mode"] == "tool_error"
    assert step_done["verification"]["verified"] is False


def test_verify_disabled(tmp_path):
    planner = FakePlanner([Task(id="t1", description="ok", tool="write_file")])
    tool_map = {"write_file": lambda **k: {"result": "claimed"}}
    llm = _make_llm(
        [{"type": "done", "content": "", "tool_calls": [_tool_call("c1", "write_file", {"path": "nope.txt"})]}],
        [{"type": "done", "content": "done", "tool_calls": None}],
    )
    auto = Autopilot(planner, llm, tool_map, [], workspace=str(tmp_path), verify=False)
    results = _run(auto)
    step_done = [e for e in _autopilot_events(results) if e["event"] == "step_done"][0]
    assert step_done["verification"] == {"verified": True, "mode": "disabled"}


def test_allowlist_blocks_tools(tmp_path):
    planner = FakePlanner([Task(id="t1", description="blocked tool", tool="danger")])
    tool_map = {"danger": lambda: {"result": "boom"}, "read_file": lambda path: {"result": "ok"}}
    llm = _make_llm(
        [{"type": "done", "content": "", "tool_calls": [_tool_call("c1", "danger", {})]}],
        [{"type": "done", "content": "fine", "tool_calls": None}],
    )
    auto = Autopilot(planner, llm, tool_map, [], workspace=str(tmp_path), tool_allowlist=["read_file"])
    results = _run(auto)

    names = _autopilot_event_names(results)
    assert "aborted" in names
    tool_results = [e for e in results if e["type"] == "tool_result"]
    assert "blocked by autopilot allowlist" in tool_results[0]["tools"][0]["result"]


def test_non_blocking_failure_continues():
    planner = FakePlanner(
        [
            Task(id="a", description="fails softly", tool="boom"),
            Task(id="b", description="still runs", tool="none"),
        ]
    )
    tool_map = {"boom": lambda: {"error": "temporary glitch"}}
    llm = _make_llm(
        [{"type": "done", "content": "", "tool_calls": [_tool_call("c1", "boom", {})]}],
        [{"type": "done", "content": "recovered", "tool_calls": None}],
        [{"type": "done", "content": "second done", "tool_calls": None}],
    )
    auto = Autopilot(planner, llm, tool_map, [])
    results = _run(auto)

    names = _autopilot_event_names(results)
    assert "aborted" not in names
    done_event = [e for e in _autopilot_events(results) if e["event"] == "done"][0]
    assert done_event["stats"] == {"total": 2, "completed": 1, "failed": 1, "skipped": 0}


def test_goal_string_passed_to_planner():
    planner = FakePlanner([Task(id="t1", description="x", tool="none")])
    llm = _make_llm([{"type": "done", "content": "ok", "tool_calls": None}])
    auto = Autopilot(planner, llm, {}, [])
    _run(auto, goal="organize my downloads")
    assert planner.created_goals == ["organize my downloads"]

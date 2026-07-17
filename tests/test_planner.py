import pytest
from core.planner import Task, _parse_tasks, Planner


class TestTask:
    def test_default_values(self):
        t = Task(id="t1", description="test")
        assert t.status == "pending"
        assert t.retries == 0
        assert t.max_retries == 3
        assert t.dependencies == []
        assert t.args == {}

    def test_to_dict(self):
        t = Task(id="t1", description="test", tool="none")
        d = t.to_dict()
        assert d["id"] == "t1"
        assert d["tool"] == "none"


class TestParseTasks:
    def test_valid_json(self):
        tasks = _parse_tasks('[{"id":"t1","description":"hello","tool":"none"}]')
        assert len(tasks) == 1
        assert tasks[0].description == "hello"

    def test_invalid_json_fallback(self):
        tasks = _parse_tasks("not json at all")
        assert len(tasks) == 1
        assert tasks[0].tool == "none"

    def test_empty_array_fallback(self):
        tasks = _parse_tasks("[]")
        assert len(tasks) == 1

    def test_multiple_tasks(self):
        json_str = '[{"id":"a","description":"first"},{"id":"b","description":"second"}]'
        tasks = _parse_tasks(json_str)
        assert len(tasks) == 2

    def test_no_json_fallback(self):
        tasks = _parse_tasks("")
        assert len(tasks) == 1

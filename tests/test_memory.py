import pytest
from core.memory.working import WorkingMemory
from core.memory.long_term import LongTermMemory, MemoryEntry
from core.memory.conversation import ConversationMemory


class TestWorkingMemory:
    def test_set_and_get(self):
        wm = WorkingMemory()
        wm.set("key", "value")
        assert wm.get("key") == "value"

    def test_get_missing(self):
        wm = WorkingMemory()
        assert wm.get("missing") is None

    def test_delete(self):
        wm = WorkingMemory()
        wm.set("key", "value")
        wm.delete("key")
        assert wm.get("key") is None

    def test_clear(self):
        wm = WorkingMemory()
        wm.set("a", "1")
        wm.set("b", "2")
        wm.clear()
        assert len(wm.get_all()) == 0

    def test_get_all(self):
        wm = WorkingMemory()
        wm.set("x", "10")
        wm.set("y", "20")
        assert wm.get_all() == {"x": "10", "y": "20"}


class TestLongTermMemory:
    @pytest.fixture
    def lm(self, tmp_path):
        path = tmp_path / "test_memory.json"
        return LongTermMemory(str(path))

    def test_store_and_recall(self, lm):
        lm.store("name", "Friday", importance=0.9)
        result = lm.recall("name")
        assert result["value"] == "Friday"

    def test_recall_missing(self, lm):
        result = lm.recall("nope")
        assert result["value"] is None

    def test_forget(self, lm):
        lm.store("temp", "value")
        lm.forget("temp")
        result = lm.recall("temp")
        assert result["value"] is None

    def test_list_all(self, lm):
        lm.store("a", "1")
        lm.store("b", "2")
        summary = lm.list_all()
        assert summary["count"] == 2

    def test_search(self, lm):
        lm.store("python_version", "3.14")
        lm.store("java_version", "21")
        results = lm.search("python")
        assert len(results) >= 1

    def test_decay(self, lm):
        lm.store("old", "data", importance=0.5)
        lm.decay(factor=0.01)
        assert lm.recall("old")["value"] is not None


class TestMemoryEntry:
    def test_score(self):
        entry = MemoryEntry("k", "v", importance=0.9)
        assert entry.score() > 0

    def test_access_increases_score(self):
        entry = MemoryEntry("k", "v", importance=0.5)
        base = entry.score()
        entry.access_count = 10
        assert entry.score() > base

    def test_to_dict_roundtrip(self):
        entry = MemoryEntry("k", "v", importance=0.7)
        data = entry.to_dict()
        restored = MemoryEntry.from_dict(data)
        assert restored.key == "k"
        assert restored.importance == 0.7


class TestConversationMemory:
    def test_add_and_get(self):
        cm = ConversationMemory(max_tokens=1000)
        cm.add("user", "hello")
        cm.add("assistant", "hi")
        assert len(cm.get_messages()) == 2

    def test_clear(self):
        cm = ConversationMemory()
        cm.add("user", "hello")
        cm.clear()
        assert len(cm.get_messages()) == 0

    def test_compress(self):
        cm = ConversationMemory(max_tokens=100)
        for i in range(60):
            cm.add("user", f"msg {i}")
        cm.compress()
        assert len(cm.get_messages()) <= 60

    def test_summarize_empty(self):
        cm = ConversationMemory()
        assert cm.summarize() == ""


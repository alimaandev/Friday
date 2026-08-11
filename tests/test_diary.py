from datetime import date, timedelta

import pytest

from core.diary import DiaryEngine


@pytest.fixture
def diary(tmp_path):
    return DiaryEngine(diary_dir=str(tmp_path / "diary"))


class TestRecord:
    def test_records_create_markdown_page(self, diary):
        path = diary.record("First entry", "Hello, diary.", kind="note")
        assert path.endswith(f"{date.today().isoformat()}.md")
        content = diary.read()
        assert "First entry" in content
        assert "Hello, diary." in content

    def test_records_append_not_overwrite(self, diary):
        diary.record("One", "body one")
        diary.record("Two", "body two")
        content = diary.read()
        assert content.count("body one") == 1
        assert content.count("body two") == 1

    def test_record_to_specific_day(self, diary):
        day = date(2026, 1, 15)
        diary.record("Old", "memory", day=day)
        assert "Old" in diary.read(day)
        assert "Old" not in diary.read()


class TestReadRecent:
    def test_read_missing_day_returns_empty(self, diary):
        assert diary.read(date(2000, 1, 1)) == ""

    def test_recent_returns_excerpts(self, diary):
        diary.record("Title line", "Behind it some body text.")
        recent = diary.recent(n=5)
        assert len(recent) == 1
        assert recent[0]["date"] == date.today().isoformat()
        assert recent[0]["excerpt"] == "Title line"

    def test_recent_skips_empty_lines(self, diary):
        diary.record("", "solo body", kind="note")
        recent = diary.recent(n=1)
        assert recent[0]["excerpt"] == "solo body"


class TestDigest:
    def test_digest_day_without_memory(self, diary, monkeypatch):
        class FakeMemory:
            def list_all(self):
                return {"entries": []}

        monkeypatch.setattr(DiaryEngine, "_get_memory_manager", staticmethod(lambda: FakeMemory()))
        text = diary.digest_day()
        assert "long-term memory" in text
        assert "0 facts" in text

    def test_digest_day_includes_notable_facts(self, diary):
        class FakeMemory:
            def list_all(self):
                return {
                    "entries": [
                        {"value": "User loves dark coffee", "importance": 0.9},
                        {"value": "Python 3.13", "importance": 0.4},
                    ]
                }

        engine = DiaryEngine(diary_dir=diary.diary_dir, memory_manager=FakeMemory())
        text = engine.digest_day()
        assert "User loves dark coffee" in text

    def test_write_day_entry_records_digest(self, diary, monkeypatch):
        class FakeMemory:
            def list_all(self):
                return {"entries": []}

        monkeypatch.setattr(DiaryEngine, "_get_memory_manager", staticmethod(lambda: FakeMemory()))
        diary.write_day_entry()
        content = diary.read()
        assert "Nightly digest" in content
        assert "long-term memory" in content


class TestMorningNote:
    def test_morning_note_empty_without_yesterday(self, diary):
        assert diary.morning_note() == ""

    def test_morning_note_returns_stripped_excerpt(self, diary):
        yesterday = date.today() - timedelta(days=1)
        diary.record("Morning", "Coffee fixed. Backlog triaged.", kind="note", day=yesterday)
        note = diary.morning_note()
        assert "Coffee fixed. Backlog triaged." in note
        assert "#" not in note

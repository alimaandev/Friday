import pytest

import core.rag as rag
from core.rag import chunk_text, ingest_document, rerank, retrieve


@pytest.fixture(autouse=True)
def _isolated_memory(tmp_path, monkeypatch):
    """Redirect the RAG store to a temp location so tests never touch real memory."""
    from core.memory import embeddings as emb_mod
    from core.memory import vector as vec_mod

    monkeypatch.setattr(emb_mod, "EMBEDDINGS_PATH", str(tmp_path / "emb.pkl"))
    monkeypatch.setattr(vec_mod, "VECTOR_STORE_PATH", str(tmp_path / "vec.pkl"))

    class FakeMemory:
        def __init__(self):
            self.embeddings = emb_mod.TfidfEngine()
            self.vector = vec_mod.VectorMemory()

    fake = FakeMemory()
    monkeypatch.setattr(rag, "get_memory_manager", lambda: fake)
    yield fake


def test_chunk_text_splits_long_document():
    text = " ".join(f"Sentence number {i} about Friday the assistant." for i in range(40))
    chunks = chunk_text(text, chunk_size=120, overlap=20)
    assert len(chunks) >= 3
    for c in chunks:
        assert len(c) <= 160


def test_chunk_text_short_text_stays_one():
    chunks = chunk_text("Short note.", chunk_size=350)
    assert chunks == ["Short note."]


def test_chunk_text_empty():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_rerank_orders_by_overlap():
    results = [
        {"id": "a", "text": "The sky is blue and the grass is green.", "score": 0.2},
        {"id": "b", "text": "Rockets launch into orbit carrying payloads.", "score": 0.5},
        {"id": "c", "text": "Blue skies over green hills.", "score": 0.1},
    ]
    out = rerank("blue sky green", results, top_k=3)
    assert out[0]["id"] in ("a", "c")
    assert all(r.get("reranked") for r in out)
    assert len(out) == 3


def test_rerank_caps_top_k():
    results = [{"id": f"r{i}", "text": f"token text {i}", "score": float(i)} for i in range(5)]
    out = rerank("token", results, top_k=2)
    assert len(out) == 2


def test_ingest_and_retrieve_document():
    text = (
        "Friday is a JARVIS-class desktop AI assistant. "
        "It has streaming chat and tool calling. "
        "It supports voice, vision, and proactive alerts. "
        "The frontend is built with React and Three.js. "
        "The backend uses Python and Quart."
    )
    res = ingest_document("Friday overview", text)
    assert res.get("success") is True
    assert res.get("chunks", 0) >= 1

    found = retrieve("what backend does Friday use", top_k=3)
    assert found["count"] >= 1
    assert any("Quart" in r.get("text", "") or "backend" in r.get("text", "") for r in found["results"])


def test_ingest_empty_document_fails():
    assert ingest_document("empty", "").get("error")

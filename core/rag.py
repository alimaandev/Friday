"""Local RAG pipeline — chunking + reranking over the memory engines.

Lets Friday ingest long documents, chunk them into overlapping passages,
store them in the vector/embedding engines, and retrieve + rerank on query.
"""

import re
import time

from core.logger import info
from core.memory import get_memory_manager

_SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")

_DEFAULT_CHUNK_SIZE = 350
_DEFAULT_OVERLAP = 60


def chunk_text(text: str, chunk_size: int = _DEFAULT_CHUNK_SIZE, overlap: int = _DEFAULT_OVERLAP) -> list[str]:
    """Split text into overlapping sentence-aligned chunks."""
    if not text:
        return []
    text = re.sub(r"\s+", " ", text).strip()
    sentences = [s.strip() for s in _SENT_SPLIT_RE.split(text) if s.strip()]
    if not sentences:
        return [text[:chunk_size]] if text else []

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for sent in sentences:
        if current and current_len + len(sent) > chunk_size:
            chunks.append(" ".join(current))
            overlap_words = current[-2:] if len(current) >= 2 else current
            current = list(overlap_words)
            current_len = sum(len(w) for w in current)
        current.append(sent)
        current_len += len(sent)

    if current:
        chunks.append(" ".join(current))

    return chunks or [text[:chunk_size]]


def _score_overlap(query_terms: set[str], passage: str) -> float:
    words = set(re.findall(r"\w+", passage.lower()))
    if not words:
        return 0.0
    return len(query_terms & words) / max(len(query_terms), 1)


def _score_position(idx: int, total: int) -> float:
    if total <= 1:
        return 0.0
    if idx == 0:
        return 0.05
    return 0.0


def rerank(query: str, results: list[dict], top_k: int = 5) -> list[dict]:
    """Rerank retrieved chunks by lexical overlap with the query."""
    query_terms = set(re.findall(r"\w+", query.lower()))
    total = max(len(results), 1)

    for i, r in enumerate(results):
        base = float(r.get("score", 0.0))
        overlap = _score_overlap(query_terms, str(r.get("text", "")))
        position = _score_position(i, total)
        r["score"] = round(base + overlap * 0.8 + position, 4)
        r["reranked"] = True

    results.sort(key=lambda x: -x.get("score", 0.0))
    return results[:top_k]


def ingest_document(title: str, text: str, source: str = "manual") -> dict:
    """Chunk a document and store all passages into the memory engines."""
    if not text.strip():
        return {"error": "document is empty"}
    chunks = chunk_text(text)
    doc_id = f"doc_{int(time.time())}"
    count = 0
    memory = get_memory_manager()

    for i, chunk in enumerate(chunks):
        meta = {"type": "document", "doc_id": doc_id, "title": title, "chunk": i, "source": source}
        memory.embeddings.store(chunk, meta)
        memory.vector.store(chunk, meta)
        count += 1

    memory.embeddings.persist()
    memory.vector.persist()
    info(f"Ingested document '{title}' as {count} chunks ({doc_id})")
    return {"success": True, "doc_id": doc_id, "chunks": count}


def retrieve(query: str, top_k: int = 5, document_only: bool = True) -> dict:
    """Retrieve + rerank chunks relevant to a query."""
    memory = get_memory_manager()
    raw = memory.embeddings.search(query, top_k=top_k * 3)
    if not raw:
        raw = memory.vector.search(query, top_k=top_k * 3)

    if document_only:
        raw = [r for r in raw if r.get("metadata", {}).get("type") == "document"]

    reranked = rerank(query, raw, top_k=top_k)
    return {
        "query": query,
        "results": reranked,
        "count": len(reranked),
    }

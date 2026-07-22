import time
from typing import Any

from core.logger import info


class MemoryConsolidator:
    def __init__(self, memory_manager):
        self._mm = memory_manager
        self._last_dedup = 0.0
        self._last_decay = 0.0

    def run_cycle(self):
        self._deduplicate()
        self._decay_old()
        self._extract_semantic_patterns()

    def _deduplicate(self):
        now = time.time()
        if now - self._last_dedup < 120:
            return
        self._last_dedup = now

        engine = self._mm.vector._engine if hasattr(self._mm.vector, '_engine') else None
        if engine is None:
            return

        entries = engine.get_entries()
        if len(entries) < 2:
            return

        merged = 0
        kept = []
        for i, a in enumerate(entries):
            skip = False
            for b in kept:
                sim = self._text_similarity(a.text, b.text)
                if sim > 0.85:
                    b.metadata["merged_from"] = b.metadata.get("merged_from", []) + [a.id]
                    b.metadata["importance"] = max(
                        b.metadata.get("importance", 0.5),
                        a.metadata.get("importance", 0.5),
                    )
                    merged += 1
                    skip = True
                    break
            if not skip:
                kept.append(a)

        if merged > 0:
            engine._entries = kept
            engine._dirty = True
            engine.persist()
            info(f"Deduplicated {merged} similar memory entries")

    def _decay_old(self):
        now = time.time()
        if now - self._last_decay < 300:
            return
        self._last_decay = now

        ltm = getattr(self._mm, 'long_term', None)
        if ltm and hasattr(ltm, 'decay'):
            before = ltm.list_all().get("count", 0)
            ltm.decay(factor=0.95)
            after = ltm.list_all().get("count", 0)
            if before != after:
                info(f"Decayed long-term memory: {before} -> {after} entries")

    def _extract_semantic_patterns(self):
        ltm = getattr(self._mm, 'long_term', None)
        if not ltm:
            return

        entries_info = ltm.list_all().get("entries", [])
        conv_entries = [e for e in entries_info if "conv_" in e.get("key", "")]
        if len(conv_entries) < 5:
            return

        patterns = self._detect_recurring_terms(conv_entries)
        for pattern_key, pattern_data in patterns.items():
            existing = ltm.recall(f"pattern_{pattern_key}")
            if existing.get("value") is None:
                ltm.store(
                    f"pattern_{pattern_key}",
                    pattern_data,
                    importance=0.6,
                )
                info(f"Extracted semantic pattern: {pattern_key}")

    def _detect_recurring_terms(self, entries: list[dict]) -> dict:
        term_freq: dict[str, int] = {}
        for e in entries:
            val = str(e.get("summary", "")).lower()
            for word in val.split():
                word = word.strip(".,!?;:'\"").strip()
                if len(word) > 3 and word not in _STOP_WORDS:
                    term_freq[word] = term_freq.get(word, 0) + 1

        patterns = {}
        for term, freq in sorted(term_freq.items(), key=lambda x: -x[1]):
            if freq >= 3 and len(patterns) < 5:
                patterns[term] = {
                    "term": term,
                    "frequency": freq,
                    "detected_at": time.time(),
                }
        return patterns

    def _text_similarity(self, a: str, b: str) -> float:
        if not a or not b:
            return 0.0
        a_tokens = set(w.lower() for w in _WORD_RE.findall(a))
        b_tokens = set(w.lower() for w in _WORD_RE.findall(b))
        if not a_tokens or not b_tokens:
            return 0.0
        intersection = a_tokens & b_tokens
        union = a_tokens | b_tokens
        jaccard = len(intersection) / len(union)
        if jaccard > 0.7:
            import difflib
            ratio = difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()
            return max(jaccard, ratio * 0.6)
        return jaccard


import re
_WORD_RE = re.compile(r"\w+")

_STOP_WORDS = {
    "this", "that", "with", "from", "have", "been", "were", "what",
    "when", "where", "which", "their", "there", "about", "would",
    "could", "should", "after", "before", "between", "other", "than",
    "then", "also", "into", "more", "some", "such", "only", "very",
    "just", "like", "over", "they", "them", "these", "those", "because",
    "user", "asked", "assistant", "responded", "friday",
}

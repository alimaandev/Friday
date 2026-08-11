"""Personal knowledge graph — entities, relations, and proactive connections.

Extracts structured knowledge from conversations and stores it in a simple
JSON graph (``memory_store/knowledge.json``). Supports:

- ``extract()`` — pull entities + relations from a turn (LLM-assisted with a
  deterministic fallback so it works fully offline)
- ``store()`` / ``query()`` — persist and search the graph
- ``continuity()`` — a session seed: "Last time you were working on…"
- ``connections()`` — proactive links between a mention and existing nodes

Everything is additive and never blocks the chat path: callers invoke it after
the response is produced, in a background task.
"""

import json
import os
import re
import time

KNOWLEDGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memory_store")
KNOWLEDGE_PATH = os.getenv("FRIDAY_KNOWLEDGE_PATH") or os.path.join(KNOWLEDGE_DIR, "knowledge.json")

_STOP = {"the", "a", "an", "is", "was", "are", "my", "your", "i", "we", "they", "it", "this", "that"}

_PATTERNS = {
    "people": re.compile(r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+){0,2}\b"),
    "projects": re.compile(
        r"(?:"
        r"(?:project|app|repo|game|tool|bot|site|api)\s+(?:called\s+|named\s+)?[\"']?([A-Za-z0-9_-]+)"
        r"|(?:the\s+)?([A-Za-z0-9_-]+)\s+(?:project|app|repo|game|tool|bot|site|api)\b"
        r")",
        re.I,
    ),
    "products": re.compile(r"\bthe\s+([a-z][a-z0-9_-]{2,20})\b"),
    "topics": re.compile(
        r"\b(?:working on|building|using|learning|trying)\s+([a-z][a-z0-9 ._-]{2,40}?)(?=\s+(?:and|with|\.|$))", re.I
    ),
}


class KnowledgeGraph:
    def __init__(self, path: str | None = None):
        self.path = path or KNOWLEDGE_PATH
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.entities: dict[str, dict] = {}
        self.relations: list[dict] = []
        self.load()

    # ─── Persistence ───────────────────────────────────────────────

    def load(self):
        if not os.path.exists(self.path):
            return
        try:
            with open(self.path, encoding="utf-8") as f:
                data = json.load(f)
            self.entities = data.get("entities", {})
            self.relations = data.get("relations", [])
        except (OSError, ValueError):
            self.entities = {}
            self.relations = []

    def persist(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"entities": self.entities, "relations": self.relations}, f, indent=2, ensure_ascii=False)

    # ─── Extraction ────────────────────────────────────────────────

    def _deterministic_extract(self, text: str) -> list[dict]:
        found: dict[str, dict] = {}

        def _add(name: str, kind: str):
            name = name.strip()
            key = name.lower()
            if not name or key in _STOP or key in found:
                return
            found[key] = {"name": name, "type": kind, "mentions": 0, "first_seen": time.time()}

        for m in _PATTERNS["projects"].findall(text):
            name = next((g for g in m if g), None)
            if name:
                _add(name, "project")
        for m in _PATTERNS["products"].findall(text):
            _add(m, "product")
        for m in _PATTERNS["topics"].findall(text):
            _add(m, "topic")
        for m in _PATTERNS["people"].findall(text):
            if m.lower() in _STOP or len(m) < 2:
                continue
            _add(m, "person")

        for ent in found.values():
            ent["mentions"] += 1
        return list(found.values())

    def extract(self, text: str, llm_call=None) -> list[dict]:
        """Extract entities + relations. Uses the LLM when provided (async), else deterministic."""
        if llm_call is not None:
            try:
                prompt = (
                    "From the following message, list entities as JSON array of "
                    "{name, type (person|project|topic|place)} and relations as array of "
                    "{subject, relation, object}. Return only JSON.\n\nMessage:\n" + text[:2000]
                )
                raw = llm_call(prompt)
                return self._parse_llm(raw)
            except Exception:
                pass
        return self._deterministic_extract(text)

    @staticmethod
    def _parse_llm(raw: str) -> list[dict]:
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if not match:
            return []
        try:
            data = json.loads(match.group(0))
        except ValueError:
            return []
        out = []
        for item in data if isinstance(data, list) else []:
            if isinstance(item, dict) and item.get("name"):
                out.append(
                    {
                        "name": str(item["name"])[:80],
                        "type": str(item.get("type", "topic"))[:20],
                        "mentions": 1,
                        "first_seen": time.time(),
                    }
                )
        return out

    # ─── Store / query ─────────────────────────────────────────────

    def store(self, text: str, source: str = "conversation", llm_call=None) -> list[dict]:
        extracted = self.extract(text, llm_call)
        added = []
        for ent in extracted:
            name = ent["name"].strip().lower()
            if not name:
                continue
            existing = self.entities.get(name)
            if existing:
                existing["mentions"] = existing.get("mentions", 0) + 1
                existing["last_seen"] = time.time()
                existing["source"] = source
            else:
                node = {**ent, "name": ent["name"].strip(), "source": source, "last_seen": time.time()}
                self.entities[name] = node
                added.append(node)
        self.persist()
        return added

    def query(self, term: str, limit: int = 10) -> list[dict]:
        t = term.lower()
        matches = [e for k, e in self.entities.items() if t in k or t in str(e.get("type", "")).lower()]
        matches.sort(key=lambda e: e.get("mentions", 0), reverse=True)
        return matches[:limit]

    def all(self) -> dict:
        entities = [dict(e) for e in self.entities.values()]
        entities.sort(key=lambda e: e.get("mentions", 0), reverse=True)
        return {"entities": entities, "relations": self.relations, "count": len(entities)}

    # ─── Continuity + connections ──────────────────────────────────

    def continuity(self, limit: int = 3) -> str:
        """Seed for a new session: the most-mentioned nodes, phrased as continuity."""
        top = sorted(self.entities.values(), key=lambda e: e.get("mentions", 0), reverse=True)[:limit]
        if not top:
            return ""
        items = ", ".join(f"**{e['name']}**" for e in top)
        return f"Context from previous sessions — you last worked on: {items}."

    def connections(self, text: str, limit: int = 4) -> list[dict]:
        """Entities already in the graph that are mentioned in ``text``."""
        t = text.lower()
        hits = []
        for key, ent in self.entities.items():
            if key in t and len(key) >= 3:
                hits.append(ent)
        hits.sort(key=lambda e: e.get("mentions", 0), reverse=True)
        return hits[:limit]

    def add_relation(self, subject: str, relation: str, obj: str):
        self.relations.append({"subject": subject, "relation": relation, "object": obj, "time": time.time()})
        self.persist()


def get_knowledge_graph() -> KnowledgeGraph:
    global _graph
    if _graph is None:
        _graph = KnowledgeGraph()
    return _graph


_graph: KnowledgeGraph | None = None

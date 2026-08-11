from typing import Any

from core.rag import ingest_document, retrieve
from plugins.base import ToolPlugin


class IngestDocumentPlugin(ToolPlugin):
    name = "ingest_document"
    description = (
        "Chunk a long document or text and store it in Friday's local knowledge base "
        "for later retrieval. Use when the user shares long articles, notes, or specs."
    )
    category = "knowledge"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Document title"},
                "text": {"type": "string", "description": "Full document text to ingest"},
            },
            "required": ["title", "text"],
        }

    def execute(self, title: str, text: str) -> dict[str, Any]:
        return ingest_document(title, text)


class RagSearchPlugin(ToolPlugin):
    name = "rag_search"
    description = (
        "Search Friday's ingested documents for chunks relevant to a query. "
        "Returns reranked passages from local documents."
    )
    category = "knowledge"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "top_k": {"type": "integer", "description": "Number of results to return", "default": 5},
            },
            "required": ["query"],
        }

    def execute(self, query: str, top_k: int = 5) -> dict[str, Any]:
        return retrieve(query, top_k=int(top_k or 5))

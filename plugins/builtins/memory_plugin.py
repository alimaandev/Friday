from core.memory import get_memory_manager
from plugins.base import ToolPlugin


class RememberPlugin(ToolPlugin):
    name = "remember"
    description = "Save a value to persistent memory (survives across sessions). Also keeps it in working memory for immediate access."
    category = "memory"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Unique key name"},
                "value": {"type": "string", "description": "Value to store"},
            },
            "required": ["key", "value"],
        }

    def execute(self, key: str, value: str) -> dict:
        return get_memory_manager().store(key, value)


class RecallPlugin(ToolPlugin):
    name = "recall"
    description = "Retrieve a value from persistent memory by key"
    category = "memory"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Key to look up"},
            },
            "required": ["key"],
        }

    def execute(self, key: str) -> dict:
        return get_memory_manager().recall(key)


class ForgetPlugin(ToolPlugin):
    name = "forget"
    description = "Delete a specific memory by key"
    category = "memory"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Key to delete"},
            },
            "required": ["key"],
        }

    def execute(self, key: str) -> dict:
        return get_memory_manager().forget(key)


class ListMemoriesPlugin(ToolPlugin):
    name = "list_memories"
    description = "List all keys stored in persistent memory, scored by importance and recency"
    category = "memory"

    def get_parameters_schema(self):
        return {"type": "object", "properties": {}, "required": []}

    def execute(self) -> dict:
        return get_memory_manager().list_all()

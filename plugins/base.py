from abc import ABC, abstractmethod
from typing import Any


class ToolPlugin(ABC):
    name: str = ""
    description: str = ""
    category: str = "general"

    @abstractmethod
    def execute(self, **kwargs) -> dict[str, Any]:
        ...

    def get_parameters_schema(self) -> dict[str, Any]:
        return {"type": "object", "properties": {}, "required": []}

    def get_tool_definition(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.get_parameters_schema(),
            },
        }

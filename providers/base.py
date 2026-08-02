from abc import ABC, abstractmethod
from collections.abc import Generator
from typing import Any


class BaseProvider(ABC):
    def __init__(self, config: dict[str, Any]):
        self.config = config

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> Generator[dict, None, None]: ...

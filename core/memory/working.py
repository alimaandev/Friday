from typing import Any


class WorkingMemory:
    def __init__(self):
        self._data: dict[str, Any] = {}

    def set(self, key: str, value: Any):
        self._data[key] = value

    def get(self, key: str) -> Any | None:
        return self._data.get(key)

    def delete(self, key: str):
        self._data.pop(key, None)

    def clear(self):
        self._data.clear()

    def get_all(self) -> dict[str, Any]:
        return dict(self._data)

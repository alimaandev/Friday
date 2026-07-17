import os
import tomllib
from typing import Any

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "providers.toml")


def load_provider_config() -> dict[str, Any]:
    if not os.path.exists(CONFIG_PATH):
        return {"default": {"provider": "ollama"}}
    with open(CONFIG_PATH, "rb") as f:
        return tomllib.load(f)


def get_active_provider(config: dict[str, Any] | None = None) -> str:
    if config is None:
        config = load_provider_config()
    return config.get("default", {}).get("provider", "ollama")


def get_provider_config(name: str | None = None) -> dict[str, Any]:
    config = load_provider_config()
    if name is None:
        name = get_active_provider(config)
    return config.get(name, {})

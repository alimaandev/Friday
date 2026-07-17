from config.providers import get_active_provider, get_provider_config
from providers.registry import get_provider_class, list_providers

import providers.ollama  # noqa: F401 — registers itself via registry
import providers.openai_compat  # noqa: F401 — registers openai/openrouter via registry


def get_provider(name: str | None = None):
    if name is None:
        name = get_active_provider()
    cls = get_provider_class(name)
    cfg = get_provider_config(name)
    return cls(cfg)

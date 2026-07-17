from config.settings import (
    OLLAMA_BASE_URL,
    MODEL,
    TEMPERATURE,
    MAX_TOKENS,
    MAX_ITERATIONS,
    LANGUAGE,
    SYSTEM_PROMPT_EN,
    SYSTEM_PROMPT_HI,
    get_system_prompt,
)

from config.providers import load_provider_config

PROVIDER_CONFIG = load_provider_config()

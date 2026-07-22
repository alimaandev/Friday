import os
import tomllib
from typing import Any

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "providers.toml")

# ─── Env var helpers ─────────────────────────────────────────────
def _load_dotenv():
    """Load .env file from project root if present."""
    root = os.path.dirname(os.path.dirname(__file__))
    env_path = os.path.join(root, ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip().strip("\"'")
            if not os.environ.get(key):
                os.environ[key] = val

_load_dotenv()


def _resolve_api_key(toml_key: str, env_var: str) -> str:
    """Resolve an API key: env var takes precedence, fall back to toml value."""
    return os.environ.get(env_var, "") or os.environ.get(toml_key, "")


def load_provider_config() -> dict[str, Any]:
    if not os.path.exists(CONFIG_PATH):
        return {"default": {"provider": "ollama"}}
    with open(CONFIG_PATH, "rb") as f:
        cfg = tomllib.load(f)

    # Override API keys from environment variables
    env_map = {
        "openai": ("api_key", "OPENAI_API_KEY"),
        "openrouter": ("api_key", "OPENROUTER_API_KEY"),
    }
    for section, (field, env_var) in env_map.items():
        if section in cfg and field in cfg[section]:
            resolved = _resolve_api_key(field, env_var)
            if resolved:
                cfg[section][field] = resolved

    return cfg


def get_active_provider(config: dict[str, Any] | None = None) -> str:
    if config is None:
        config = load_provider_config()
    return config.get("default", {}).get("provider", "ollama")


def get_provider_config(name: str | None = None) -> dict[str, Any]:
    config = load_provider_config()
    if name is None:
        name = get_active_provider(config)
    return config.get(name, {})

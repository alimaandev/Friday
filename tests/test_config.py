import pytest
from config import OLLAMA_BASE_URL, MODEL, MAX_ITERATIONS, get_system_prompt


class TestConfig:
    def test_ollama_url_default(self):
        assert OLLAMA_BASE_URL == "http://localhost:11434"

    def test_model_name(self):
        assert isinstance(MODEL, str)
        assert len(MODEL) > 0

    def test_max_iterations(self):
        assert MAX_ITERATIONS > 0

    def test_system_prompt_english(self):
        prompt = get_system_prompt("english")
        assert "USE TOOLS" in prompt

    def test_system_prompt_hinglish(self):
        prompt = get_system_prompt("hinglish")
        assert "USE KAR" in prompt or "TOOLS USE KAR" in prompt

    def test_system_prompt_default(self):
        prompt = get_system_prompt()
        assert len(prompt) > 100

    def test_provider_config(self):
        from config.providers import get_active_provider, get_provider_config
        provider = get_active_provider()
        assert provider in ("openrouter", "ollama"), f"unexpected provider {provider}"
        cfg = get_provider_config(provider)
        assert isinstance(cfg, dict)

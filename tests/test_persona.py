from core.persona import PERSONA_KEYS, PERSONAS, get_persona_config, get_persona_prompt


class TestPersona:
    def test_has_all_personas(self):
        assert "friday" in PERSONAS
        assert "jarvis" in PERSONAS
        assert "cortana" in PERSONAS

    def test_persona_keys(self):
        assert set(PERSONA_KEYS) == {"friday", "jarvis", "cortana"}

    def test_each_persona_has_required_fields(self):
        for key, p in PERSONAS.items():
            assert "name" in p
            assert "label" in p
            assert "description" in p
            assert "prompt" in p
            assert "tts_rate" in p
            assert "tts_pitch" in p

    def test_get_persona_prompt_valid(self):
        prompt = get_persona_prompt("jarvis")
        assert "J.A.R.V.I.S." in prompt
        assert len(prompt) > 50

    def test_get_persona_prompt_invalid_fallsback(self):
        prompt = get_persona_prompt("nonexistent")
        assert "FRIDAY" in prompt

    def test_get_persona_config_valid(self):
        cfg = get_persona_config("cortana")
        assert cfg["name"] == "Cortana"
        assert cfg["tts_pitch"] == 1.05

    def test_get_persona_config_invalid_fallsback(self):
        cfg = get_persona_config("bad_key")
        assert cfg["name"] == "Friday"

    def test_tts_rates_are_reasonable(self):
        for p in PERSONAS.values():
            assert 0.5 <= p["tts_rate"] <= 2.0
            assert 0.5 <= p["tts_pitch"] <= 2.0

    def test_prompts_are_unique(self):
        prompts = [p["prompt"] for p in PERSONAS.values()]
        assert len(set(prompts)) == len(prompts)

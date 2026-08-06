from core.vision import HAS_PIL, VisionEngine


class TestVisionEngine:
    def test_engine_initializes(self):
        engine = VisionEngine()
        assert engine is not None
        assert engine._screen_interval == 10
        assert engine._last_screen_hash is None

    def test_capture_screen(self):
        engine = VisionEngine()
        result = engine.capture_screen()
        if result is None:
            return  # headless env (no display)
        assert "image" in result
        assert result["width"] > 0

    def test_screen_changed(self):
        engine = VisionEngine()
        result = engine.screen_changed_since_last_check()
        if HAS_PIL:
            assert isinstance(result, bool)
        else:
            assert result is False

    def test_analyze_image_returns_string(self):
        engine = VisionEngine()
        result = engine.analyze_image("not-a-base64-string")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_extract_text_returns_none_without_ocr(self):
        engine = VisionEngine()
        result = engine.extract_text("aaaa")
        assert result is None

    def test_describe_screen_returns_dict(self):
        engine = VisionEngine()
        result = engine.describe_screen()
        assert isinstance(result, dict)
        if not HAS_PIL:
            assert "error" in result
        else:
            assert "description" in result or "error" in result

    def test_analyze_camera_frame_returns_description(self):
        engine = VisionEngine()
        result = engine.analyze_camera_frame("aaaa")
        assert "description" in result
        assert "timestamp" in result

"""Vision engine for Friday — screen analysis, image understanding, and OCR."""

import base64
import io
import time

try:
    from PIL import Image, ImageGrab

    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Optional OCR
try:
    import pytesseract

    HAS_OCR = True
except ImportError:
    HAS_OCR = False


class VisionEngine:
    """Analyze screenshots and camera frames using LLM vision + optional OCR."""

    def __init__(self):
        self._last_screen_hash: str | None = None
        self._screen_interval = 10  # min seconds between auto-analyses

    # ─── Screen capture ───────────────────────────────────────────

    def capture_screen(self) -> dict | None:
        """Capture the screen as a base64 PNG. Returns dict or None on failure."""
        if not HAS_PIL:
            return None
        try:
            img = ImageGrab.grab()
            buf = io.BytesIO()
            img.save(buf, format="PNG", optimize=True)
            b64 = base64.b64encode(buf.getvalue()).decode()
            return {
                "image": b64,
                "width": img.width,
                "height": img.height,
                "timestamp": time.time(),
            }
        except Exception:
            return None

    def screen_changed_since_last_check(self) -> bool:
        """Quick MD5 comparison to detect screen changes."""
        if not HAS_PIL:
            return False
        try:
            import hashlib

            img = ImageGrab.grab()
            h = hashlib.md5(img.tobytes()).hexdigest()
            if h != self._last_screen_hash:
                self._last_screen_hash = h
                return True
            return False
        except Exception:
            return False

    # ─── Image analysis via LLM ───────────────────────────────────

    def analyze_image(self, image_base64: str, prompt: str | None = None) -> str:
        """Describe an image using the LLM vision endpoint."""
        if not prompt:
            prompt = "Describe what you see in this image in 2-3 sentences."
        try:
            from providers import get_provider

            provider = get_provider()
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}",
                                "detail": "low",
                            },
                        },
                    ],
                }
            ]
            result = ""
            for event in provider.chat(messages):
                content = event.get("content", "")
                if content:
                    result += content
            return result.strip() or "No description available."
        except Exception as e:
            return f"Vision analysis unavailable: {e}"

    def extract_text(self, image_base64: str) -> str | None:
        """Extract text from an image using OCR (pytesseract)."""
        if not HAS_OCR:
            return None
        try:
            img_data = base64.b64decode(image_base64)
            img = Image.open(io.BytesIO(img_data))
            text = pytesseract.image_to_string(img)
            return text.strip() or None
        except Exception:
            return None

    def describe_screen(self) -> dict:
        """Capture screen + run analysis. Returns combined result."""
        screen = self.capture_screen()
        if not screen:
            return {"error": "Screen capture unavailable (PIL required)."}
        description = self.analyze_image(
            screen["image"],
            prompt="Describe what's on this computer screen. What application is open? What content is visible? Be concise (2-3 sentences).",
        )
        text = self.extract_text(screen["image"])
        return {
            "description": description,
            "text": text,
            "width": screen["width"],
            "height": screen["height"],
            "timestamp": screen["timestamp"],
        }

    def analyze_camera_frame(self, image_base64: str) -> dict:
        """Analyze a webcam frame for objects, faces, text."""
        description = self.analyze_image(
            image_base64,
            prompt="Describe what you see in this camera image. Are there any people? Objects? Text? Be concise (2-3 sentences).",
        )
        text = self.extract_text(image_base64)
        return {
            "description": description,
            "text": text,
            "timestamp": time.time(),
        }


_engine: VisionEngine | None = None


def get_vision_engine() -> VisionEngine:
    global _engine
    if _engine is None:
        _engine = VisionEngine()
    return _engine

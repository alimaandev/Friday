import threading
import time

_tts_engine = None
_tts_lock = threading.Lock()
_speaking = False
_stop_flag = False


def _init_tts():
    global _tts_engine
    try:
        import pyttsx3
        _tts_engine = pyttsx3.init(driverName="sapi5")
        _tts_engine.setProperty("rate", 180)
        _tts_engine.setProperty("volume", 0.9)
    except Exception:
        pass


def speak(text: str) -> dict:
    if _tts_engine is None:
        _init_tts()
    if _tts_engine is None:
        return {"success": False, "error": "TTS not available"}

    def _say():
        global _speaking
        with _tts_lock:
            _speaking = True
            try:
                _tts_engine.say(text)
                _tts_engine.runAndWait()
            except Exception:
                pass
            _speaking = False

    threading.Thread(target=_say, daemon=True).start()
    return {"success": True, "message": "Speaking..."}


def speak_interruptible(text: str) -> dict:
    if _tts_engine is None:
        _init_tts()
    if _tts_engine is None:
        return {"success": False, "error": "TTS not available"}

    global _stop_flag
    _stop_flag = False

    def _say():
        global _speaking, _stop_flag
        with _tts_lock:
            _speaking = True
            sentences = text.replace("? ", ". ").replace("! ", ". ").split(". ")
            for sentence in sentences:
                if _stop_flag:
                    break
                if not sentence.strip():
                    continue
                try:
                    _tts_engine.say(sentence.strip())
                    _tts_engine.runAndWait()
                except Exception:
                    pass
            _speaking = False

    threading.Thread(target=_say, daemon=True).start()
    return {"success": True, "message": "Speaking (interruptible)..."}


def stop_speaking() -> dict:
    global _stop_flag
    _stop_flag = True
    return {"success": True, "message": "Speech stopped"}


def is_speaking() -> bool:
    return _speaking

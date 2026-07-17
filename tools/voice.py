from voice.stt import listen as _listen, is_voice_available as _check_avail
from voice.tts import speak as _speak


def speak(text: str) -> dict:
    return _speak(text)


def listen() -> dict:
    return _listen()


def is_voice_available() -> bool:
    return _check_avail()

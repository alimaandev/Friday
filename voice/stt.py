import io
import wave

import numpy as np

SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
SILENCE_DURATION = 1.5
ENERGY_THRESHOLD = 300
MAX_RECORD_SECONDS = 20


def _rms(data):
    if len(data) == 0:
        return 0
    return np.sqrt(np.mean(data.astype(np.float64) ** 2))


def listen() -> dict:
    try:
        import sounddevice as sd
        import speech_recognition as sr

        recorded = []
        silence_start = None
        voice_detected = False
        total_samples = 0
        max_samples = SAMPLE_RATE * MAX_RECORD_SECONDS

        def callback(indata, frames, time_info, status):
            nonlocal silence_start, voice_detected, total_samples
            if status:
                return
            energy = _rms(indata[:, 0])
            total_samples += frames

            if energy > ENERGY_THRESHOLD:
                voice_detected = True
                silence_start = None
                recorded.append(indata.copy())
            elif voice_detected:
                if silence_start is None:
                    silence_start = total_samples
                recorded.append(indata.copy())

            if total_samples >= max_samples:
                raise sd.CallbackAbort()

        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
            blocksize=CHUNK_SIZE,
            callback=callback,
        ):
            sd.sleep(int(MAX_RECORD_SECONDS * 1000))

        if not voice_detected or not recorded:
            return {"text": "", "success": False, "error": "No speech detected (timeout)"}

        audio_data = np.concatenate(recorded)
        trim_ms = int(SILENCE_DURATION * SAMPLE_RATE)
        if len(audio_data) > trim_ms:
            audio_data = audio_data[:-trim_ms]

        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_data.tobytes())
        buf.seek(0)

        recognizer = sr.Recognizer()
        with sr.AudioFile(buf) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio)
        return {"text": text, "success": True}

    except Exception as e:
        err_msg = str(e)
        if "UnknownValue" in type(e).__name__:
            return {"text": "", "success": False, "error": "Could not understand audio"}
        return {"text": "", "success": False, "error": err_msg}


def is_voice_available() -> bool:
    try:
        import sounddevice as sd
        sd.query_devices(kind="input")
        return True
    except Exception:
        return False

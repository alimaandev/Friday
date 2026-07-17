import numpy as np


class VoiceActivityDetector:
    def __init__(self, sample_rate: int = 16000, threshold: int = 300):
        self.sample_rate = sample_rate
        self.threshold = threshold

    def is_speech(self, audio_chunk: np.ndarray) -> bool:
        if len(audio_chunk) == 0:
            return False
        energy = np.sqrt(np.mean(audio_chunk.astype(np.float64) ** 2))
        return energy > self.threshold

    def detect_activity(self, audio: np.ndarray) -> list[tuple[int, int]]:
        frame_size = int(self.sample_rate * 0.03)
        segments = []
        in_speech = False
        start = 0

        for i in range(0, len(audio), frame_size):
            frame = audio[i:i + frame_size]
            speech = self.is_speech(frame)
            if speech and not in_speech:
                start = i
                in_speech = True
            elif not speech and in_speech:
                if i - start > self.sample_rate * 0.1:
                    segments.append((start, i))
                in_speech = False

        if in_speech:
            segments.append((start, len(audio)))
        return segments

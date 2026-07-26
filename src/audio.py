import threading
from collections import deque
from typing import Optional, Callable, List
import time


class AudioStreamProcessor:
    def __init__(self, sample_rate: int = 16000, chunk_size: int = 2048):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.audio_buffer = deque(maxlen=10000)
        self.is_recording = False
        self.interrupt_detected = False
        self.audio_thread = None
        self.callbacks = []

    def add_callback(self, callback: Callable[[List[int]], None]):
        self.callbacks.append(callback)

    def on_audio_chunk(self, audio_data: bytes):
        self.audio_buffer.append(audio_data)
        for callback in self.callbacks:
            try:
                callback(audio_data)
            except Exception as e:
                print(f"Callback error: {e}")

    def detect_silence(self, audio_data: bytes, threshold: int = 500) -> bool:
        if not audio_data or len(audio_data) < 2:
            return True

        max_amplitude = 0
        for i in range(0, len(audio_data), 2):
            if i + 1 < len(audio_data):
                value = int.from_bytes(audio_data[i:i+2], byteorder='little', signed=True)
                max_amplitude = max(max_amplitude, abs(value))

        return max_amplitude < threshold

    def detect_speech_boundary(self, audio_chunks: deque, window_size: int = 5) -> bool:
        if len(audio_chunks) < window_size:
            return False

        recent = list(audio_chunks)[-window_size:]
        silence_count = sum(1 for chunk in recent if self.detect_silence(chunk))

        return silence_count >= window_size // 2

    def detect_interruption(self, current_speaking: bool) -> bool:
        if not current_speaking:
            return False

        recent_chunks = list(self.audio_buffer)[-10:]
        has_speech = not all(self.detect_silence(chunk) for chunk in recent_chunks)

        return has_speech

    def get_transcription_audio(self) -> bytes:
        return b''.join(self.audio_buffer)

    def clear_buffer(self):
        self.audio_buffer.clear()
        self.interrupt_detected = False

    def start_recording(self):
        self.is_recording = True
        self.interrupt_detected = False
        self.audio_buffer.clear()

    def stop_recording(self):
        self.is_recording = False


class InterruptHandler:
    def __init__(self, audio_processor: AudioStreamProcessor):
        self.audio_processor = audio_processor
        self.assistant_speaking = False
        self.monitoring = False
        self.interrupt_callbacks = []

    def add_interrupt_callback(self, callback: Callable[[], None]):
        self.interrupt_callbacks.append(callback)

    def start_monitoring(self):
        self.monitoring = True
        self.assistant_speaking = True

    def stop_monitoring(self):
        self.monitoring = False
        self.assistant_speaking = False

    def check_for_interrupt(self) -> bool:
        if not self.monitoring or not self.assistant_speaking:
            return False

        if self.audio_processor.detect_interruption(True):
            self.interrupt_detected = True
            for callback in self.interrupt_callbacks:
                callback()
            return True
        return False

    def handle_interrupt(self) -> Optional[str]:
        self.stop_monitoring()
        captured_audio = self.audio_processor.get_transcription_audio()
        return captured_audio if captured_audio else None


class MockAudioStream:
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.is_active = True

    def read(self, num_frames: int) -> bytes:
        import time
        time.sleep(0.01)
        return b'\x00' * (num_frames * 2)

    def stop_stream(self):
        self.is_active = False

    def close(self):
        pass

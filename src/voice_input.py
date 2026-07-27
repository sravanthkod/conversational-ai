import speech_recognition as sr
import threading
from typing import Optional, Callable

class VoiceInputHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000  # Adjust for your mic
        self.is_listening = False
        self.last_input = None
        self.on_input_callback = None

    def capture_voice_input(self, timeout: int = 10) -> Optional[str]:
        """
        Capture audio from microphone and convert to text using Google Speech Recognition.

        Args:
            timeout: Max seconds to listen for speech

        Returns:
            Transcribed text, or None if error
        """
        try:
            with sr.Microphone() as source:
                print("\n🎤 Listening... (speak now)")

                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                # Capture audio
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)

                print("⏳ Processing audio...")

                # Convert to text using Google Speech Recognition
                text = self.recognizer.recognize_google(audio)
                print(f"✓ Recognized: {text}\n")
                return text

        except sr.UnknownValueError:
            print("\n❌ Could not understand audio. Please try again.\n")
            return None
        except sr.RequestException as e:
            print(f"\n❌ Error accessing speech recognition service: {e}\n")
            return None
        except Exception as e:
            print(f"\n❌ Microphone error: {e}\n")
            print("   Tip: Install pyaudio: pip install pyaudio")
            return None

    def capture_voice_input_async(self, callback: Callable[[str], None]):
        """
        Capture voice input in background thread and call callback.

        Args:
            callback: Function to call with transcribed text
        """
        def listen_thread():
            text = self.capture_voice_input()
            if text and callback:
                callback(text)

        thread = threading.Thread(target=listen_thread, daemon=True)
        thread.start()

    def stream_microphone_input(self):
        """
        Continuously stream microphone input.
        Yields transcribed text as user speaks.
        """
        try:
            with sr.Microphone() as source:
                print("\n🎤 Microphone streaming started...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)

                while True:
                    try:
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                        text = self.recognizer.recognize_google(audio)

                        if text:
                            print(f"🎤 {text}")
                            yield text
                    except sr.UnknownValueError:
                        pass  # Silence, continue listening
                    except sr.RequestException:
                        break
        except Exception as e:
            print(f"Microphone error: {e}")

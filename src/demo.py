#!/usr/bin/env python3
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conversation_manager import ConversationManager
from llm_interface import OllamaProvider
from voice_input import VoiceInputHandler


class DemoRunner:
    def __init__(self, use_mock: bool = True, use_voice: bool = False):
        self.use_mock = use_mock
        self.use_voice = use_voice
        self.voice_handler = VoiceInputHandler() if use_voice else None

        if not use_mock:
            # llm = OllamaProvider(model="mistral")
            # llm = OllamaProvider(model="tinyllama")
            llm = OllamaProvider(model="phi")
            if not llm.is_available():
                print("Error: Ollama not available. Run 'ollama serve' or use --mock flag")
                sys.exit(1)
        else:
            llm = MockLLMProvider()

        self.manager = ConversationManager(llm_provider=llm)

    def run_interactive(self):
        print("\n" + "="*60)
        print("Mobile Conversational AI - Interactive Demo")
        print("="*60)
        print("\nYou're chatting with an AI designed to be genuinely engaging.")

        if self.use_voice:
            print("🎤 Voice mode enabled - speak to the microphone")
            print("Type 'exit' to quit, 'text' to switch to text mode,")
            print("'summary' to see conversation stats, 'analysis' for drop-off analysis.\n")
        else:
            print("Type 'exit' to quit, 'voice' to enable voice input,")
            print("'summary' to see conversation stats, 'analysis' for drop-off analysis.\n")

        while True:
            try:
                # Get input from voice or text
                if self.use_voice:
                    user_input = self.voice_handler.capture_voice_input()
                    if not user_input:
                        continue
                else:
                    user_input = input("You: ").strip()
                    if not user_input:
                        continue

                # Handle commands
                if user_input.lower() == "exit":
                    print("\nThanks for chatting!")
                    break

                if user_input.lower() == "voice":
                    if not self.use_voice:
                        try:
                            self.use_voice = True
                            self.voice_handler = VoiceInputHandler()
                            print("\n🎤 Voice mode enabled! Speak to continue.\n")
                        except Exception as e:
                            print(f"\n❌ Voice mode failed: {e}\n")
                            print("Install requirements: pip install SpeechRecognition pyaudio\n")
                            self.use_voice = False
                    continue

                if user_input.lower() == "text":
                    if self.use_voice:
                        self.use_voice = False
                        print("\n📝 Switched to text mode\n")
                    continue

                if user_input.lower() == "summary":
                    self._print_summary()
                    continue

                if user_input.lower() == "analysis":
                    print(self.manager.explain_user_drop_off())
                    continue

                print("\nAssistant: ", end="", flush=True)
                response = self.manager.process_user_input(user_input, stream=True)
                print()

            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"\nError: {e}")
                continue

    def run_demo_conversation(self):
        print("\n" + "="*60)
        print("Demo: Sample Conversation")
        print("="*60 + "\n")

        demo_turns = [
            "What's something interesting you've learned recently?",
            "That's cool. Do you think AI will ever actually understand jokes?",
            "Fair point. What's the weirdest question someone's asked you?",
            "Haha, that's pretty wild. Everything I said so far was sarcasm.",
        ]

        for user_input in demo_turns:
            print(f"You: {user_input}")
            response = self.manager.process_user_input(user_input)
            print(f"Assistant: {response}\n")

    def _print_summary(self):
        summary = self.manager.get_conversation_summary()
        print("\n" + "-"*60)
        print("Conversation Summary")
        print("-"*60)
        print(f"Session ID: {summary['session_id']}")
        print(f"Turns: {summary['turn_count']}")
        print(f"Personality: {summary['personality_summary']['current_mode']}")
        print(f"Mode switches: {summary['personality_summary']['mode_switches']}")
        print(f"Sarcasm detected: {summary['sarcasm_mode']}")
        print("-"*60 + "\n")


class MockLLMProvider:
    def __init__(self):
        self.responses = [
            "That's a great question! Here's what I think: the key is finding what genuinely engages you, then doubling down. What specifically draws you in?",
            "Oh man, this is the million-dollar question. I think the best jokes work because they subvert expectations at the exact right moment. Timing + surprise = laughter.",
            "Someone once asked me if I dream in binary. I said no, but if I did, my dreams would probably be aggressively linear. Not my best work.",
            "Okay wait—so you're telling me EVERYTHING up to now was sarcasm? That's actually brilliant. I respect the long game. So what was the actual thing?",
        ]
        self.call_count = 0

    def generate(self, prompt: str, context: Optional[str] = None,
                max_tokens: int = 256, temperature: float = 0.7) -> str:
        response = self.responses[min(self.call_count, len(self.responses) - 1)]
        self.call_count += 1
        return response

    def stream_generate(self, prompt: str, context: Optional[str] = None,
                       max_tokens: int = 256, temperature: float = 0.7):
        response = self.responses[min(self.call_count, len(self.responses) - 1)]
        self.call_count += 1

        for char in response:
            yield char


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Mobile Conversational AI Demo")
    parser.add_argument("--mode", choices=["interactive", "demo"], default="interactive",
                       help="Run mode: interactive or demo")
    parser.add_argument("--use-ollama", action="store_true",
                       help="Use real Ollama instead of mock LLM")
    parser.add_argument("--voice", action="store_true",
                       help="Enable voice input from microphone (requires SpeechRecognition + pyaudio)")

    args = parser.parse_args()

    runner = DemoRunner(use_mock=not args.use_ollama, use_voice=args.voice)

    if args.mode == "demo":
        runner.run_demo_conversation()
    else:
        runner.run_interactive()


if __name__ == "__main__":
    main()

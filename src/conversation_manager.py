import uuid
import time
from typing import Optional, List, Dict
from datetime import datetime

try:
    from .memory import ConversationalMemory
    from .personality import PersonalityEngine, PersonalityMode
    from .llm_interface import OllamaProvider, ContextManager, ResponseProcessor
    from .audio import AudioStreamProcessor, InterruptHandler
except ImportError:
    from memory import ConversationalMemory
    from personality import PersonalityEngine, PersonalityMode
    from llm_interface import OllamaProvider, ContextManager, ResponseProcessor
    from audio import AudioStreamProcessor, InterruptHandler


class ConversationManager:
    def __init__(self, llm_provider=None, memory_db: str = "conversation_memory.db"):
        self.session_id = str(uuid.uuid4())
        self.memory = ConversationalMemory(memory_db)
        self.personality_engine = PersonalityEngine()
        self.llm_provider = llm_provider or OllamaProvider()
        self.context_manager = ContextManager()
        self.audio_processor = AudioStreamProcessor()
        self.interrupt_handler = InterruptHandler(self.audio_processor)
        self.response_processor = ResponseProcessor()

        self.conversation_history: List[Dict] = []
        self.turn_count = 0
        self.sarcasm_mode = False

        self.memory.create_session(self.session_id)

    def process_user_input(self, user_input: str, stream: bool = False) -> str:
        self.turn_count += 1
        self.audio_processor.start_recording()

        user_input = user_input.strip()
        if not user_input:
            return "I'm ready to listen. What's on your mind?"

        sarcasm_detected = self.personality_engine.detect_sarcasm(user_input)

        if self.sarcasm_mode and "sarcasm" in user_input.lower():
            recovery_response = self.personality_engine.handle_sarcasm_recovery(
                [t['assistant_response'] for t in self.conversation_history]
            )
            self.sarcasm_mode = False
            return recovery_response

        personality_mode = self.personality_engine.select_personality_mode(
            user_input, self.turn_count, sarcasm_detected
        )

        context_hints = self.memory.get_contextual_hints(self.session_id)

        prompt = self.context_manager.build_prompt(
            user_input,
            self.conversation_history,
            personality_mode.value,
            context_hints
        )

        if stream:
            response = self._generate_streaming_response(prompt)
        else:
            response = self.llm_provider.generate(prompt, max_tokens=256, temperature=0.8)

        response = self.response_processor.clean_response(response)

        emotional_context = self.response_processor.extract_emotion(response)

        if sarcasm_detected:
            self.sarcasm_mode = True
            self.memory.add_turn(
                self.session_id, self.turn_count, user_input, response,
                emotional_context=emotional_context,
                user_tone="sarcastic",
                sarcasm_detected=True
            )
        else:
            self.memory.add_turn(
                self.session_id, self.turn_count, user_input, response,
                emotional_context=emotional_context,
                user_tone=personality_mode.value
            )

        self.conversation_history.append({
            "turn": self.turn_count,
            "user_input": user_input,
            "assistant_response": response,
            "personality_mode": personality_mode.value,
            "sarcasm_detected": sarcasm_detected,
            "timestamp": datetime.now().isoformat()
        })

        self.audio_processor.stop_recording()

        if self.turn_count == 3:
            self._evaluate_engagement()

        return response

    def _generate_streaming_response(self, prompt: str) -> str:
        full_response = ""
        try:
            for chunk in self.llm_provider.stream_generate(prompt, max_tokens=256, temperature=0.8):
                full_response += chunk
                print(chunk, end="", flush=True)

                if self.interrupt_handler.check_for_interrupt():
                    print("\n[Interrupted by user input]")
                    self.interrupt_handler.stop_monitoring()
                    break
        except Exception as e:
            full_response = f"Error during streaming: {str(e)}"

        print()
        return full_response.strip()

    def handle_interruption(self) -> str:
        captured_audio = self.interrupt_handler.handle_interrupt()
        return "[Assistant interrupted by user. Ready for new input.]"

    def _evaluate_engagement(self):
        if self.turn_count == 3:
            engagement_score = self._calculate_engagement_score()
            if engagement_score < 0.5:
                print("\n[Note: Low engagement detected at turn 3. Adjusting personality...]")
                self.personality_engine.current_mode = PersonalityMode.PLAYFUL

    def _calculate_engagement_score(self) -> float:
        if len(self.conversation_history) < 2:
            return 0.5

        recent_turns = self.conversation_history[-2:]
        avg_response_length = sum(len(t.get('user_input', '')) for t in recent_turns) / len(recent_turns)
        has_questions = sum(1 for t in recent_turns if '?' in t.get('user_input', '')) / len(recent_turns)

        engagement = (min(avg_response_length / 50, 1.0) * 0.5) + (has_questions * 0.5)
        return engagement

    def get_conversation_summary(self) -> Dict:
        return {
            "session_id": self.session_id,
            "turn_count": self.turn_count,
            "conversation_history": self.conversation_history,
            "personality_summary": self.personality_engine.get_personality_summary(),
            "sarcasm_mode": self.sarcasm_mode,
        }

    def explain_user_drop_off(self) -> str:
        return """Why users might drop off after 3 turns:

1. CONVERSATION MOMENTUM LOSS
   - Generic responses feel impersonal
   - Assistant not building on previous context
   - Personality becomes repetitive

2. LACK OF GENUINE CURIOSITY
   - Assistant just answers, doesn't ask back
   - No follow-up questions showing real interest
   - Conversation feels one-directional

3. CONTEXT COLLAPSE
   - Assistant forgets what matters to the user
   - Important details not referenced later
   - Feels like talking to an amnesiac

4. EMOTIONAL TONE MISMATCH
   - Assistant tone doesn't match user's mood
   - Tries to be funny when user needs empathy
   - Generic cheerfulness feels tone-deaf

MEASUREMENT:
   - Session continuation rate past turn 3
   - User question rate (engagement signal)
   - Sentiment consistency between turns
   - Mention of prior context in responses

FIXES:
   - Implement personality adaptation based on conversation flow
   - Add proactive follow-up questions
   - Maintain emotional context across turns
   - Use humor strategically, not by default
"""

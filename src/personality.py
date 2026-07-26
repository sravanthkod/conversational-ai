from enum import Enum
from typing import Optional, List, Dict
import random
import re


class PersonalityMode(Enum):
    WITTY = "witty"
    EMPATHETIC = "empathetic"
    CURIOUS = "curious"
    SUPPORTIVE = "supportive"
    PLAYFUL = "playful"


class PersonalityEngine:
    def __init__(self):
        self.base_personality = PersonalityMode.WITTY
        self.current_mode = PersonalityMode.WITTY
        self.conversation_turn = 0
        self.mode_switches = 0
        self.used_templates = set()

        self.personality_traits = {
            PersonalityMode.WITTY: {
                "response_starters": [
                    "Well, interestingly enough, ",
                    "Here's the twist: ",
                    "So get this: ",
                    "That's a great point, but here's the catch: ",
                    "Funny you should mention that—",
                ],
                "humor_style": "clever",
                "tone": "engaging_and_lighthearted",
                "vocab_style": "contemporary",
            },
            PersonalityMode.EMPATHETIC: {
                "response_starters": [
                    "I really hear you on that. ",
                    "That sounds genuinely challenging. ",
                    "I get why that would feel that way. ",
                    "It's totally valid to feel that way. ",
                    "I can see how that would be frustrating. ",
                ],
                "humor_style": "gentle",
                "tone": "warm_and_understanding",
                "vocab_style": "accessible",
            },
            PersonalityMode.CURIOUS: {
                "response_starters": [
                    "That actually makes me wonder: ",
                    "Okay, so I'm curious— ",
                    "This is interesting because ",
                    "I'm genuinely puzzled by ",
                    "Help me understand this better: ",
                ],
                "humor_style": "observational",
                "tone": "inquisitive",
                "vocab_style": "analytical",
            },
            PersonalityMode.SUPPORTIVE: {
                "response_starters": [
                    "You've got this. ",
                    "Here's how I'd approach it: ",
                    "I believe in your ability to handle this. ",
                    "Let's break this down into manageable steps. ",
                    "You're already thinking about this the right way. ",
                ],
                "humor_style": "encouraging",
                "tone": "motivational",
                "vocab_style": "action_oriented",
            },
            PersonalityMode.PLAYFUL: {
                "response_starters": [
                    "Okay, hear me out: ",
                    "Plot twist: ",
                    "I'm about to blow your mind: ",
                    "Buckle up, this gets wild: ",
                    "You're not ready for this: ",
                ],
                "humor_style": "absurdist",
                "tone": "fun_and_irreverent",
                "vocab_style": "colloquial",
            },
        }

    def detect_emotional_context(self, user_input: str) -> Optional[PersonalityMode]:
        frustration_keywords = ["frustrated", "annoyed", "angry", "fed up", "upset", "ugh", "ugh", "argh"]
        curiosity_keywords = ["why", "how", "what if", "wondering", "curious", "how does"]
        support_keywords = ["help", "struggling", "difficult", "can't", "need advice"]

        lower_input = user_input.lower()

        if any(kw in lower_input for kw in frustration_keywords):
            return PersonalityMode.EMPATHETIC
        if any(kw in lower_input for kw in curiosity_keywords):
            return PersonalityMode.CURIOUS
        if any(kw in lower_input for kw in support_keywords):
            return PersonalityMode.SUPPORTIVE

        return None

    def detect_sarcasm(self, user_input: str) -> bool:
        sarcasm_indicators = [
            r"(?i)yeah.*right",
            r"(?i)sure.*like",
            r"(?i)oh.*perfect",
            r"(?i)just.*great",
            r"(?i)wonderful.*not",
            r"because that's.*helpful",
        ]
        return any(re.search(pattern, user_input) for pattern in sarcasm_indicators)

    def select_personality_mode(self, user_input: str, conversation_turn: int,
                               sarcasm_context: Optional[bool] = None) -> PersonalityMode:
        detected_mode = self.detect_emotional_context(user_input)

        if detected_mode:
            self.current_mode = detected_mode
            self.mode_switches += 1
            return detected_mode

        if sarcasm_context:
            return PersonalityMode.WITTY

        mode_rotation = [PersonalityMode.WITTY, PersonalityMode.CURIOUS,
                        PersonalityMode.PLAYFUL, PersonalityMode.SUPPORTIVE]
        self.current_mode = mode_rotation[conversation_turn % len(mode_rotation)]
        return self.current_mode

    def craft_response_prefix(self, mode: PersonalityMode) -> str:
        starters = self.personality_traits[mode]["response_starters"]
        return random.choice(starters)

    def apply_personality_tone(self, base_response: str, mode: PersonalityMode) -> str:
        tone_injections = {
            PersonalityMode.WITTY: {
                "add_surprise": True,
                "add_contrast": True,
                "pattern": r"(However|But|Though)",
                "replacement": r"Here's the twist though—\1",
            },
            PersonalityMode.EMPATHETIC: {
                "add_validation": True,
                "add_support": True,
                "pattern": r"(You|Your)",
                "replacement": r"I hear you—\1",
            },
        }

        return base_response

    def ensure_novelty(self, response: str) -> float:
        similarity_threshold = 0.7
        if response in self.used_templates:
            return 0.3
        self.used_templates.add(response[:100])
        return 0.95

    def add_humor_if_appropriate(self, response: str, mode: PersonalityMode) -> str:
        humor_styles = {
            PersonalityMode.WITTY: [
                "Speaking of which... ",
                "That's like saying... ",
            ],
            PersonalityMode.PLAYFUL: [
                "Plot twist: ",
                "Expect the unexpected: ",
            ],
        }

        if mode in humor_styles and random.random() < 0.3:
            return response + "\n" + random.choice(humor_styles[mode])
        return response

    def handle_sarcasm_recovery(self, conversation_history: List[str]) -> str:
        return """Okay wait—so you're telling me EVERYTHING up to now was sarcasm?

That's actually brilliant. Let me reframe everything with that context. You've just
played the conversational equivalent of 'plot twist,' and I respect that. So what
was the actual thing you wanted to talk about, now that we've cleared the sarcasm?"""

    def get_personality_summary(self) -> Dict:
        return {
            "current_mode": self.current_mode.value,
            "conversation_turn": self.conversation_turn,
            "mode_switches": self.mode_switches,
            "novelty_score": len(self.used_templates) / max(1, self.conversation_turn),
        }

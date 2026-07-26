# Google Colab Notebook - Mobile Conversational AI Demo
# Copy all cells below into a Colab notebook in order

# ============================================
# CELL 1: Install Dependencies
# ============================================
"""
!pip install requests numpy sqlalchemy pydantic python-dotenv pyyaml -q
print("✓ Dependencies installed")
"""

# ============================================
# CELL 2: Setup Project Structure
# ============================================
"""
import os
os.chdir('/content')
os.makedirs('conversational_ai/src', exist_ok=True)
os.chdir('conversational_ai')
print(f"✓ Working directory: {os.getcwd()}")
"""

# ============================================
# CELL 3: Create memory.py
# ============================================
"""
memory_py_code = '''import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass
import hashlib

@dataclass
class ConversationTurn:
    user_input: str
    assistant_response: str
    timestamp: str
    turn_id: int
    emotional_context: Optional[str] = None
    user_tone: Optional[str] = None
    sarcasm_detected: bool = False

class ConversationalMemory:
    def __init__(self, db_path: str = "conversation_memory.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_turns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    turn_number INTEGER NOT NULL,
                    user_input TEXT NOT NULL,
                    assistant_response TEXT NOT NULL,
                    emotional_context TEXT,
                    user_tone TEXT,
                    sarcasm_detected BOOLEAN DEFAULT 0
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS humor_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    joke_hash TEXT UNIQUE NOT NULL,
                    used_count INTEGER DEFAULT 1
                )
            """)
            conn.commit()

    def create_session(self, session_id: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO conversations (session_id) VALUES (?)", (session_id,))
            conn.commit()

    def add_turn(self, session_id: str, turn_number: int, user_input: str,
                 assistant_response: str, emotional_context: Optional[str] = None,
                 user_tone: Optional[str] = None, sarcasm_detected: bool = False):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversation_turns
                (session_id, turn_number, user_input, assistant_response,
                 emotional_context, user_tone, sarcasm_detected)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (session_id, turn_number, user_input, assistant_response,
                  emotional_context, user_tone, sarcasm_detected))
            conn.commit()

    def get_conversation_history(self, session_id: str, max_turns: int = 10):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM conversation_turns
                WHERE session_id = ?
                ORDER BY turn_number DESC
                LIMIT ?
            """, (session_id, max_turns))
            return cursor.fetchall()

    def log_joke(self, joke_content: str):
        joke_hash = hashlib.md5(joke_content.encode()).hexdigest()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT used_count FROM humor_history WHERE joke_hash = ?", (joke_hash,))
            result = cursor.fetchone()
            if result:
                cursor.execute("UPDATE humor_history SET used_count = used_count + 1 WHERE joke_hash = ?", (joke_hash,))
            else:
                cursor.execute("INSERT INTO humor_history (joke_hash) VALUES (?)", (joke_hash,))
            conn.commit()

    def get_joke_diversity_score(self, joke_content: str) -> float:
        joke_hash = hashlib.md5(joke_content.encode()).hexdigest()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT used_count FROM humor_history WHERE joke_hash = ?", (joke_hash,))
            result = cursor.fetchone()
            if result:
                used_count = result[0]
                return 1.0 / (1.0 + used_count)
            return 1.0
'''

with open('src/memory.py', 'w') as f:
    f.write(memory_py_code)
print("✓ Created memory.py")
"""

# ============================================
# CELL 4: Create personality.py
# ============================================
"""
personality_py_code = '''from enum import Enum
from typing import Optional, List
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
        self.current_mode = PersonalityMode.WITTY
        self.conversation_turn = 0
        self.personality_traits = {
            PersonalityMode.WITTY: {
                "response_starters": [
                    "Well, interestingly enough, ",
                    "Here's the twist: ",
                    "So get this: ",
                ],
                "tone": "engaging_and_lighthearted",
            },
            PersonalityMode.EMPATHETIC: {
                "response_starters": [
                    "I really hear you on that. ",
                    "That sounds genuinely challenging. ",
                    "I get why that would feel that way. ",
                ],
                "tone": "warm_and_understanding",
            },
            PersonalityMode.CURIOUS: {
                "response_starters": [
                    "That actually makes me wonder: ",
                    "Okay, so I'm curious— ",
                    "This is interesting because ",
                ],
                "tone": "inquisitive",
            },
            PersonalityMode.SUPPORTIVE: {
                "response_starters": [
                    "You've got this. ",
                    "Here's how I'd approach it: ",
                    "You're already thinking about this the right way. ",
                ],
                "tone": "motivational",
            },
            PersonalityMode.PLAYFUL: {
                "response_starters": [
                    "Okay, hear me out: ",
                    "Plot twist: ",
                    "I'm about to blow your mind: ",
                ],
                "tone": "fun_and_irreverent",
            },
        }

    def detect_emotional_context(self, user_input: str) -> Optional[PersonalityMode]:
        frustration_keywords = ["frustrated", "annoyed", "angry", "upset"]
        curiosity_keywords = ["why", "how", "what if", "curious"]
        support_keywords = ["help", "struggling", "difficult"]

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
        ]
        return any(re.search(pattern, user_input) for pattern in sarcasm_indicators)

    def select_personality_mode(self, user_input: str, conversation_turn: int) -> PersonalityMode:
        detected_mode = self.detect_emotional_context(user_input)
        if detected_mode:
            return detected_mode

        mode_rotation = [PersonalityMode.WITTY, PersonalityMode.CURIOUS,
                        PersonalityMode.PLAYFUL, PersonalityMode.SUPPORTIVE]
        return mode_rotation[conversation_turn % len(mode_rotation)]

    def craft_response_prefix(self, mode: PersonalityMode) -> str:
        starters = self.personality_traits[mode]["response_starters"]
        return random.choice(starters)

    def handle_sarcasm_recovery(self):
        return """Okay wait—so you're telling me EVERYTHING up to now was sarcasm?
That's actually brilliant. Let me reframe everything with that context."""
'''

with open('src/personality.py', 'w') as f:
    f.write(personality_py_code)
print("✓ Created personality.py")
"""

# ============================================
# CELL 5: Create conversation_manager.py
# ============================================
"""
conversation_py_code = '''import uuid
from typing import Optional, List, Dict
from datetime import datetime

try:
    from memory import ConversationalMemory
    from personality import PersonalityEngine, PersonalityMode
except ImportError:
    from .memory import ConversationalMemory
    from .personality import PersonalityEngine, PersonalityMode

class ConversationManager:
    def __init__(self, llm_provider=None):
        self.session_id = str(uuid.uuid4())
        self.memory = ConversationalMemory()
        self.personality_engine = PersonalityEngine()
        self.llm_provider = llm_provider
        self.conversation_history: List[Dict] = []
        self.turn_count = 0
        self.sarcasm_mode = False

        self.memory.create_session(self.session_id)

    def process_user_input(self, user_input: str) -> str:
        self.turn_count += 1
        user_input = user_input.strip()

        if not user_input:
            return "I'm ready to listen. What's on your mind?"

        sarcasm_detected = self.personality_engine.detect_sarcasm(user_input)

        if self.sarcasm_mode and "sarcasm" in user_input.lower():
            recovery_response = self.personality_engine.handle_sarcasm_recovery()
            self.sarcasm_mode = False
            return recovery_response

        personality_mode = self.personality_engine.select_personality_mode(
            user_input, self.turn_count
        )

        if self.llm_provider:
            response = self.llm_provider.generate("", max_tokens=256, temperature=0.8)
        else:
            response = "That's an interesting perspective."

        if sarcasm_detected:
            self.sarcasm_mode = True

        self.memory.add_turn(
            self.session_id, self.turn_count, user_input, response,
            user_tone=personality_mode.value,
            sarcasm_detected=sarcasm_detected
        )

        self.conversation_history.append({
            "turn": self.turn_count,
            "user_input": user_input,
            "assistant_response": response,
            "personality_mode": personality_mode.value,
            "sarcasm_detected": sarcasm_detected,
        })

        return response

    def get_conversation_summary(self) -> Dict:
        return {
            "session_id": self.session_id,
            "turn_count": self.turn_count,
            "conversation_history": self.conversation_history,
            "personality_summary": {
                "current_mode": self.personality_engine.current_mode.value,
            },
            "sarcasm_mode": self.sarcasm_mode,
        }
'''

with open('src/conversation_manager.py', 'w') as f:
    f.write(conversation_py_code)
print("✓ Created conversation_manager.py")
"""

# ============================================
# CELL 6: Create Mock LLM Provider
# ============================================
"""
class MockLLMProvider:
    def __init__(self):
        self.responses = [
            "That's a great question! Here's what I think: the key is finding what genuinely engages you. What specifically draws you in?",
            "Oh man, this is the million-dollar question. I think the best jokes work because they subvert expectations. Timing + surprise = laughter.",
            "Someone once asked me if I dream in binary. I said no, but my dreams would probably be aggressively linear. Not my best work.",
            "Okay wait—so you're telling me EVERYTHING up to now was sarcasm? That's actually brilliant. Let me reframe everything with that context.",
        ]
        self.call_count = 0

    def generate(self, prompt: str, context=None, max_tokens: int = 256, temperature: float = 0.7) -> str:
        response = self.responses[min(self.call_count, len(self.responses) - 1)]
        self.call_count += 1
        return response

print("✓ MockLLMProvider created")
"""

# ============================================
# CELL 7: Run the Demo
# ============================================
"""
import sys
sys.path.insert(0, '/content/conversational_ai')

from conversation_manager import ConversationManager

# Create conversation manager
manager = ConversationManager(llm_provider=MockLLMProvider())

print("\\n" + "="*60)
print("Mobile Conversational AI - Colab Demo")
print("="*60 + "\\n")

# Demo conversation
demo_turns = [
    "What's something interesting you've learned recently?",
    "That's cool. Do you think AI will ever understand jokes?",
    "Fair point. What's the weirdest question someone's asked you?",
    "Everything I said so far was sarcasm.",
]

for user_input in demo_turns:
    print(f"You: {user_input}")
    response = manager.process_user_input(user_input)
    print(f"Assistant: {response}\\n")

# Show summary
summary = manager.get_conversation_summary()
print("-"*60)
print(f"Session ID: {summary['session_id'][:12]}...")
print(f"Turns: {summary['turn_count']}")
print(f"Personality Mode: {summary['personality_summary']['current_mode']}")
print(f"Sarcasm Detected: {summary['sarcasm_mode']}")
print("-"*60)
"""

# ============================================
# CELL 8: Interactive Chat (Optional)
# ============================================
"""
# Reset for interactive mode
manager = ConversationManager(llm_provider=MockLLMProvider())

# Test multi-turn
test_inputs = [
    "I'm learning to code",
    "But it's really frustrating",
    "Do you have any tips?"
]

print("\\n" + "="*60)
print("Interactive Mode Test")
print("="*60 + "\\n")

for user_input in test_inputs:
    response = manager.process_user_input(user_input)
    print(f"You: {user_input}")
    print(f"Assistant: {response}\\n")
"""

# ============================================
# END OF NOTEBOOK
# ============================================

print("""
COLAB NOTEBOOK READY!

Copy the cells above into a Google Colab notebook:
1. Go to colab.research.google.com
2. Create a new notebook
3. Copy each cell above (between the ''' markers) into separate Colab cells
4. Run each cell in order
5. The demo will run automatically in Cell 7!

For interactive mode, use Cell 8 to chat freely.
""")

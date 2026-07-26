# Running in Google Colab

## Option 1: Quick Start (5 minutes)

### Step 1: Create New Colab Notebook
Go to [colab.research.google.com](https://colab.research.google.com)

### Step 2: Install Dependencies
```python
!pip install requests numpy sqlalchemy pydantic python-dotenv pyyaml -q
```

### Step 3: Download Project from GitHub
```python
!git clone https://github.com/YOUR_USERNAME/conversational-ai.git
%cd conversational-ai
```

Or if you don't have it on GitHub, copy the files directly (see Option 2).

### Step 4: Run the Demo
```python
import sys
sys.path.insert(0, '/content/conversational-ai')

from src.conversation_manager import ConversationManager
from src.demo import DemoRunner

# Run demo conversation
runner = DemoRunner(use_mock=True)
runner.run_demo_conversation()
```

---

## Option 2: Manual Setup (Copy-Paste Code)

### Cell 1: Install & Create Structure
```python
!pip install requests numpy sqlalchemy pydantic python-dotenv pyyaml -q

import os
import subprocess

os.chdir('/content')
os.makedirs('conversational_ai/src', exist_ok=True)
os.chdir('conversational_ai')

print("✓ Project structure created")
print(f"✓ Working directory: {os.getcwd()}")
```

### Cell 2: Create src/__init__.py
```python
init_code = '''"""Mobile Conversational AI - Next Generation System"""
__version__ = "1.0.0"

try:
    from .conversation_manager import ConversationManager
    from .memory import ConversationalMemory
    from .personality import PersonalityEngine, PersonalityMode
    from .llm_interface import OllamaProvider, ContextManager
    from .audio import AudioStreamProcessor, InterruptHandler
except ImportError as e:
    print(f"Warning: Could not import all modules: {e}")

__all__ = [
    "ConversationManager",
    "ConversationalMemory",
    "PersonalityEngine",
    "PersonalityMode",
    "OllamaProvider",
    "ContextManager",
    "AudioStreamProcessor",
    "InterruptHandler",
]
'''

with open('src/__init__.py', 'w') as f:
    f.write(init_code)

print("✓ Created src/__init__.py")
```

### Cell 3: Create src/memory.py
```python
memory_code = '''import sqlite3
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
            cursor.execute(\'\'\'
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_profile JSON
                )
            \'\'\')
            cursor.execute(\'\'\'
                CREATE TABLE IF NOT EXISTS conversation_turns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    turn_number INTEGER NOT NULL,
                    user_input TEXT NOT NULL,
                    assistant_response TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    emotional_context TEXT,
                    user_tone TEXT,
                    sarcasm_detected BOOLEAN DEFAULT 0,
                    FOREIGN KEY (session_id) REFERENCES conversations(session_id)
                )
            \'\'\')
            cursor.execute(\'\'\'
                CREATE TABLE IF NOT EXISTS humor_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    joke_hash TEXT UNIQUE NOT NULL,
                    joke_content TEXT NOT NULL,
                    used_count INTEGER DEFAULT 1,
                    first_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES conversations(session_id)
                )
            \'\'\')
            cursor.execute(\'\'\'
                CREATE TABLE IF NOT EXISTS contextual_hints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    context TEXT NOT NULL,
                    turn_introduced INTEGER,
                    importance_score REAL DEFAULT 0.5,
                    FOREIGN KEY (session_id) REFERENCES conversations(session_id)
                )
            \'\'\')
            conn.commit()

    def create_session(self, session_id: str, user_profile: Optional[Dict] = None) -> str:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(\'\'\'
                INSERT INTO conversations (session_id, user_profile)
                VALUES (?, ?)
            \'\'\', (session_id, json.dumps(user_profile or {})))
            conn.commit()
        return session_id

    def add_turn(self, session_id: str, turn_number: int, user_input: str,
                 assistant_response: str, emotional_context: Optional[str] = None,
                 user_tone: Optional[str] = None, sarcasm_detected: bool = False):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(\'\'\'
                INSERT INTO conversation_turns
                (session_id, turn_number, user_input, assistant_response,
                 emotional_context, user_tone, sarcasm_detected)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            \'\'\', (session_id, turn_number, user_input, assistant_response,
                  emotional_context, user_tone, sarcasm_detected))
            conn.commit()

    def get_conversation_history(self, session_id: str, max_turns: int = 10) -> List[ConversationTurn]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(\'\'\'
                SELECT * FROM conversation_turns
                WHERE session_id = ?
                ORDER BY turn_number DESC
                LIMIT ?
            \'\'\', (session_id, max_turns))
            rows = cursor.fetchall()
            return [ConversationTurn(
                user_input=row[\'user_input\'],
                assistant_response=row[\'assistant_response\'],
                timestamp=row[\'timestamp\'],
                turn_id=row[\'id\'],
                emotional_context=row[\'emotional_context\'],
                user_tone=row[\'user_tone\'],
                sarcasm_detected=bool(row[\'sarcasm_detected\'])
            ) for row in reversed(rows)]

    def log_joke(self, session_id: str, joke_content: str):
        joke_hash = hashlib.md5(joke_content.encode()).hexdigest()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(\'SELECT used_count FROM humor_history WHERE joke_hash = ?\', (joke_hash,))
            result = cursor.fetchone()
            if result:
                cursor.execute(\'\'\'
                    UPDATE humor_history
                    SET used_count = used_count + 1, last_used = CURRENT_TIMESTAMP
                    WHERE joke_hash = ?
                \'\'\', (joke_hash,))
            else:
                cursor.execute(\'\'\'
                    INSERT INTO humor_history (session_id, joke_hash, joke_content)
                    VALUES (?, ?, ?)
                \'\'\', (session_id, joke_hash, joke_content))
            conn.commit()

    def get_joke_diversity_score(self, joke_content: str) -> float:
        joke_hash = hashlib.md5(joke_content.encode()).hexdigest()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(\'\'\'
                SELECT used_count,
                       CAST((julianday(\'now\') - julianday(last_used)) AS INTEGER) as days_since_used
                FROM humor_history
                WHERE joke_hash = ?
            \'\'\', (joke_hash,))
            result = cursor.fetchone()
            if result:
                used_count, days_since = result
                return 1.0 / (1.0 + used_count) * (1.0 + days_since / 30.0)
            return 1.0
'''

with open('src/memory.py', 'w') as f:
    f.write(memory_code)

print("✓ Created src/memory.py")
```

### Cell 4-7: Create Remaining Modules
(Copy from the GitHub repo or from the original project files)

### Cell 8: Run Demo
```python
import sys
sys.path.insert(0, '/content/conversational_ai')

# Import after path is set
from src.conversation_manager import ConversationManager

# Create mock LLM provider for Colab
class MockLLMProvider:
    def __init__(self):
        self.responses = [
            "That's a great question! The key is finding what genuinely engages you. What specifically draws you in?",
            "Oh man, this is important. I think the best ideas work because they connect unexpected dots at the right moment.",
            "Someone once asked me something similar. I realized the answer wasn't obvious until we dug deeper.",
            "Wait—so everything I just heard was sarcasm? That's brilliant, honestly. Let me reframe this entire thing.",
        ]
        self.call_count = 0

    def generate(self, prompt: str, context=None, max_tokens: int = 256, temperature: float = 0.7) -> str:
        response = self.responses[min(self.call_count, len(self.responses) - 1)]
        self.call_count += 1
        return response

    def stream_generate(self, prompt: str, context=None, max_tokens: int = 256, temperature: float = 0.7):
        response = self.responses[min(self.call_count, len(self.responses) - 1)]
        self.call_count += 1
        for char in response:
            yield char

# Run conversation
manager = ConversationManager(llm_provider=MockLLMProvider())

print("\n" + "="*60)
print("Mobile Conversational AI - Colab Demo")
print("="*60 + "\n")

# Demo turns
demo_turns = [
    "What's something interesting you've learned recently?",
    "That's cool. Do you think AI will ever truly understand ideas?",
    "Fair point. What's the weirdest question someone's asked you?",
    "Everything I said so far was sarcasm.",
]

for user_input in demo_turns:
    print(f"You: {user_input}")
    response = manager.process_user_input(user_input)
    print(f"Assistant: {response}\n")

# Show summary
summary = manager.get_conversation_summary()
print("\n" + "-"*60)
print(f"Turns: {summary['turn_count']}")
print(f"Personality Mode: {summary['personality_summary']['current_mode']}")
print(f"Sarcasm Detected: {summary['sarcasm_mode']}")
print("-"*60)
```

---

## What Works in Colab

✅ **Fully Working**:
- Conversation management
- Personality engine (5 modes)
- Memory system (SQLite)
- Emotion detection
- Sarcasm recovery
- Response generation (with mock LLM)
- All demos and examples

⚠️ **With Limitations**:
- PyAudio (falls back to mock audio, which is fine)
- Ollama (could run but requires additional setup)
- Streaming audio input (not available in Colab environment)

❌ **Not Available**:
- Real microphone input (Colab doesn't expose audio hardware)
- Direct system audio playback

---

## Interactive Chat in Colab

```python
# For multi-turn conversation with input
from src.conversation_manager import ConversationManager
from src.demo import MockLLMProvider

manager = ConversationManager(llm_provider=MockLLMProvider())

def chat(user_input):
    response = manager.process_user_input(user_input)
    return response

# Test it
print(chat("Tell me something interesting"))
print(chat("That's cool. How does that work?"))
print(chat("What about edge cases?"))
```

---

## Sharing Your Colab Notebook

Once you create it:
1. Click **Share** (top right)
2. Get the link
3. Share it with interviewers
4. They can run cells directly without installing anything

---

## Expected Output in Colab

```
============================================================
Mobile Conversational AI - Colab Demo
============================================================

You: What's something interesting you've learned recently?
Assistant: That's a great question! The key is finding what genuinely 
           engages you. What specifically draws you in?

You: That's cool. Do you think AI will ever truly understand ideas?
Assistant: Oh man, this is important. I think the best ideas work because 
           they connect unexpected dots at the right moment.

You: Fair point. What's the weirdest question someone's asked you?
Assistant: Someone once asked me something similar. I realized the answer 
           wasn't obvious until we dug deeper.

You: Everything I said so far was sarcasm.
Assistant: Wait—so everything I just heard was sarcasm? That's brilliant, 
           honestly. Let me reframe this entire thing.

------------------------------------------------------------
Turns: 4
Personality Mode: playful
Sarcasm Detected: True
------------------------------------------------------------
```

---

## Pro Tips for Colab

1. **Save to Drive** for persistence:
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   # Files in /content/drive/My Drive stay after session ends
   ```

2. **Use forms for interactive input**:
   ```python
   #@markdown Enter your message:
   user_input = "" #@param {type:"string"}
   response = manager.process_user_input(user_input)
   print(f"Assistant: {response}")
   ```

3. **Export results**:
   ```python
   summary = manager.get_conversation_summary()
   import json
   with open('/content/conversation.json', 'w') as f:
       json.dump(summary, f, indent=2)
   ```

---

## Next Steps

1. Create Colab notebook
2. Copy this setup
3. Run the demo
4. Customize for your interview demo
5. Share the link with interviewers

They can click "Run cell" and see it work without installing anything!

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict
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
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_profile JSON
                )
            ''')
            cursor.execute('''
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
            ''')
            cursor.execute('''
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
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contextual_hints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    context TEXT NOT NULL,
                    turn_introduced INTEGER,
                    importance_score REAL DEFAULT 0.5,
                    FOREIGN KEY (session_id) REFERENCES conversations(session_id)
                )
            ''')
            conn.commit()

    def create_session(self, session_id: str, user_profile: Optional[Dict] = None) -> str:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO conversations (session_id, user_profile)
                VALUES (?, ?)
            ''', (session_id, json.dumps(user_profile or {})))
            conn.commit()
        return session_id

    def add_turn(self, session_id: str, turn_number: int, user_input: str,
                 assistant_response: str, emotional_context: Optional[str] = None,
                 user_tone: Optional[str] = None, sarcasm_detected: bool = False):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO conversation_turns
                (session_id, turn_number, user_input, assistant_response,
                 emotional_context, user_tone, sarcasm_detected)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, turn_number, user_input, assistant_response,
                  emotional_context, user_tone, sarcasm_detected))
            conn.commit()

    def get_conversation_history(self, session_id: str, max_turns: int = 10) -> List[ConversationTurn]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM conversation_turns
                WHERE session_id = ?
                ORDER BY turn_number DESC
                LIMIT ?
            ''', (session_id, max_turns))
            rows = cursor.fetchall()
            return [ConversationTurn(
                user_input=row['user_input'],
                assistant_response=row['assistant_response'],
                timestamp=row['timestamp'],
                turn_id=row['id'],
                emotional_context=row['emotional_context'],
                user_tone=row['user_tone'],
                sarcasm_detected=bool(row['sarcasm_detected'])
            ) for row in reversed(rows)]

    def log_joke(self, session_id: str, joke_content: str):
        joke_hash = hashlib.md5(joke_content.encode()).hexdigest()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT used_count FROM humor_history WHERE joke_hash = ?', (joke_hash,))
            result = cursor.fetchone()
            if result:
                cursor.execute('''
                    UPDATE humor_history
                    SET used_count = used_count + 1, last_used = CURRENT_TIMESTAMP
                    WHERE joke_hash = ?
                ''', (joke_hash,))
            else:
                cursor.execute('''
                    INSERT INTO humor_history (session_id, joke_hash, joke_content)
                    VALUES (?, ?, ?)
                ''', (session_id, joke_hash, joke_content))
            conn.commit()

    def get_joke_diversity_score(self, joke_content: str) -> float:
        joke_hash = hashlib.md5(joke_content.encode()).hexdigest()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT used_count,
                       CAST((julianday('now') - julianday(last_used)) AS INTEGER) as days_since_used
                FROM humor_history
                WHERE joke_hash = ?
            ''', (joke_hash,))
            result = cursor.fetchone()
            if result:
                used_count, days_since = result
                return 1.0 / (1.0 + used_count) * (1.0 + days_since / 30.0)
            return 1.0

    def add_contextual_hint(self, session_id: str, topic: str, context: str, turn_introduced: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO contextual_hints (session_id, topic, context, turn_introduced)
                VALUES (?, ?, ?, ?)
            ''', (session_id, topic, context, turn_introduced))
            conn.commit()

    def get_contextual_hints(self, session_id: str) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM contextual_hints
                WHERE session_id = ?
                ORDER BY importance_score DESC
                LIMIT 5
            ''', (session_id,))
            return [dict(row) for row in cursor.fetchall()]

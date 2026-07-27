import requests
import json
from typing import Optional, List, Dict, Iterator
from abc import ABC, abstractmethod
import time


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, context: Optional[str] = None,
                max_tokens: int = 256, temperature: float = 0.7) -> str:
        pass

    @abstractmethod
    def stream_generate(self, prompt: str, context: Optional[str] = None,
                       max_tokens: int = 256, temperature: float = 0.7) -> Iterator[str]:
        pass


class OllamaProvider(LLMProvider):
    def __init__(self, model: str = "mistral", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.endpoint = f"{base_url}/api/generate"

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

    # def generate(self, prompt: str, context: Optional[str] = None,
    #             max_tokens: int = 256, temperature: float = 0.7) -> str:
    #     full_prompt = f"{context}\n\n{prompt}" if context else prompt

    #     payload = {
    #         "model": self.model,
    #         "prompt": full_prompt,
    #         "stream": False,
    #         "temperature": temperature,
    #         "num_predict": max_tokens,
    #     }

    #     try:
    #         response = requests.post(self.endpoint, json=payload, timeout=30)
    #         if response.status_code == 200:
    #             return response.json().get("response", "").strip()
    #     except requests.exceptions.RequestException as e:
    #         return f"Error generating response: {str(e)}"

    #     return ""

    def generate(self, prompt: str, context: Optional[str] = None,
            max_tokens: int = 256, temperature: float = 0.7) -> str:
    
    # SIMPLIFY: Don't include context in request
        payload = {
            "model": self.model,
            "prompt": prompt,  # Just the prompt, no context
            "stream": False,
            "temperature": 0.5,  # Lower temperature
            "num_predict": 100,  # Smaller response
            "top_k": 40,
            "top_p": 0.9,
        }
        
        try:
            response = requests.post(self.endpoint, json=payload, timeout=60)
            if response.status_code == 200:
                return response.json().get("response", "").strip()
        except requests.exceptions.RequestException as e:
            return f"Error: {str(e)}"
        
        return ""


    def stream_generate(self, prompt: str, context: Optional[str] = None,
                       max_tokens: int = 256, temperature: float = 0.7) -> Iterator[str]:
        full_prompt = f"{context}\n\n{prompt}" if context else prompt

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": True,
            "temperature": temperature,
            "num_predict": max_tokens,
        }

        try:
            response = requests.post(self.endpoint, json=payload, timeout=30, stream=True)
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]
                    if data.get("done", False):
                        break
        except requests.exceptions.RequestException:
            yield "Error: Could not reach LLM service."


class ContextManager:
    def __init__(self, max_context_turns: int = 5):
        self.max_context_turns = max_context_turns
        self.system_prompt = """You are a witty, emotionally intelligent conversational AI assistant.
Your responses should be:
- Naturally engaging and conversational
- Occasionally humorous without being forced
- Emotionally aware of the user's context
- Concise (under 150 words typically)
- Never generic ("I'm sorry to hear that" is banned)
- Focused on adding genuine value, not just acknowledging

When appropriate, show genuine curiosity, playful wit, or deep understanding.
Avoid corporate-sounding language. Be authentic."""

    def build_context(self, conversation_history: List[Dict]) -> str:
        context_parts = [self.system_prompt]

        for turn in conversation_history[-self.max_context_turns:]:
            context_parts.append(f"User: {turn['user_input']}")
            context_parts.append(f"Assistant: {turn['assistant_response']}")

        return "\n".join(context_parts)

    def build_prompt(self, user_input: str, conversation_history: List[Dict],
                    personality_mode: str, contextual_hints: Optional[List[Dict]] = None) -> str:
        context = self.build_context(conversation_history)

        hints_text = ""
        if contextual_hints:
            hints_text = "\nContext hints: " + ", ".join(
                [f"{h['topic']}: {h['context']}" for h in contextual_hints[:3]]
            )

        prompt = f"""{context}

{hints_text}

Personality mode: {personality_mode}
User: {user_input}
Assistant:"""
        return prompt


class ResponseProcessor:
    @staticmethod
    def clean_response(response: str) -> str:
        response = response.strip()
        if response.endswith("User:"):
            response = response.rsplit("User:", 1)[0].strip()
        return response

    @staticmethod
    def extract_emotion(response: str) -> Optional[str]:
        emotions = {
            "joyful": ["amazing", "wonderful", "fantastic", "love"],
            "curious": ["wonder", "question", "interesting", "puzzle"],
            "empathetic": ["understand", "feel", "hear", "acknowledge"],
        }

        lower_response = response.lower()
        for emotion, keywords in emotions.items():
            if any(kw in lower_response for kw in keywords):
                return emotion
        return None

    @staticmethod
    def detect_topic_shift(current: str, previous: str) -> bool:
        current_words = set(current.lower().split())
        previous_words = set(previous.lower().split())
        overlap = len(current_words & previous_words) / (len(current_words) + 0.01)
        return overlap < 0.3

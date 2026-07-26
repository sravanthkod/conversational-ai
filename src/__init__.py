"""Mobile Conversational AI - Next Generation System"""

__version__ = "1.0.0"
__author__ = "AI Research Team"

from .conversation_manager import ConversationManager
from .memory import ConversationalMemory
from .personality import PersonalityEngine, PersonalityMode
from .llm_interface import OllamaProvider, ContextManager
from .audio import AudioStreamProcessor, InterruptHandler

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

from flask import Flask, render_template, request, jsonify
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.conversation_manager import ConversationManager
from src.llm_interface import OllamaProvider

app = Flask(__name__)

# Global conversation manager
manager = None

class MockLLMProvider:
    """Mock LLM for demo - responds without needing Ollama"""
    def __init__(self):
        self.responses = [
            "That's a great question! Here's what I think: the key is finding what genuinely engages you, then doubling down. What specifically draws you in?",
            "Oh man, this is the million-dollar question. I think the best jokes work because they subvert expectations at the exact right moment. Timing + surprise = laughter.",
            "Someone once asked me if I dream in binary. I said no, but if I did, my dreams would probably be aggressively linear. Not my best work.",
            "That's a fascinating perspective. I hadn't thought of it that way before.",
            "Okay wait—so you're telling me EVERYTHING up to now was sarcasm? That's actually brilliant. Let me reframe everything with that context. You've just played the conversational equivalent of 'plot twist,' and I respect that.",
            "Here's the thing about that: it's more nuanced than it first appears.",
            "I really hear you on that. That sounds genuinely challenging.",
            "That's interesting because it suggests something deeper is going on.",
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


def init_manager():
    """Initialize conversation manager with mock LLM"""
    global manager
    if manager is None:
        manager = ConversationManager(llm_provider=MockLLMProvider())
    return manager


@app.route('/')
def index():
    """Serve the chat interface"""
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Process user input and return assistant response"""
    init_manager()

    data = request.json
    user_input = data.get('message', '').strip()

    if not user_input:
        return jsonify({'error': 'Empty message'}), 400

    try:
        # Get response
        response = manager.process_user_input(user_input)

        # Get current state
        summary = manager.get_conversation_summary()
        personality_mode = summary['personality_summary']['current_mode']
        turn_count = summary['turn_count']
        sarcasm_mode = summary['sarcasm_mode']

        # Get emotion context from last turn
        history = manager.conversation_history
        last_turn = history[-1] if history else {}
        emotional_context = last_turn.get('emotional_context', 'neutral')

        return jsonify({
            'response': response,
            'personality_mode': personality_mode,
            'turn_count': turn_count,
            'sarcasm_detected': sarcasm_mode,
            'emotional_context': emotional_context,
            'success': True
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset conversation"""
    global manager
    manager = None
    return jsonify({'success': True, 'message': 'Conversation reset'})


@app.route('/api/analysis', methods=['GET'])
def analysis():
    """Get failure analysis"""
    init_manager()
    analysis_text = manager.explain_user_drop_off()
    return jsonify({'analysis': analysis_text})


@app.route('/api/summary', methods=['GET'])
def summary():
    """Get conversation summary"""
    init_manager()
    summary_data = manager.get_conversation_summary()
    return jsonify(summary_data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

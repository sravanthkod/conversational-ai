# Ollama Setup Guide - Make It REAL

This guide gets you from zero to running real LLM responses (not mocks) in your conversational AI system.

---

## What is Ollama?

Ollama runs open-source LLMs locally on your machine. No API keys, no cloud costs, no internet required after first download.

- **Free**: Completely free
- **Private**: Your data never leaves your machine
- **Fast**: Runs on CPU/GPU
- **Easy**: One-click setup

---

## Step 1: Install Ollama

### **macOS**
```bash
brew install ollama
# or download from https://ollama.ai
```

### **Windows**
```bash
# Download from https://ollama.ai/download/windows
# Run the installer
# Or via Chocolatey:
choco install ollama
```

### **Linux**
```bash
curl https://ollama.ai/install.sh | sh
```

Verify:
```bash
ollama --version
```

---

## Step 2: Download a Model

Ollama provides several models. **Mistral** is our recommendation (fast, good quality):

```bash
ollama pull mistral
```

Other options:
- `ollama pull llama2` - Excellent quality, slower
- `ollama pull neural-chat` - Fast, conversational
- `ollama pull dolphin-mixtral` - Creative, good for personality

**First download takes 3-10 minutes** (model is 4-13GB depending on choice)

---

## Step 3: Start the Ollama Server

### **Terminal 1: Start Ollama Service**
```bash
ollama serve
```

You should see:
```
time=2024-01-15T10:00:00Z level=INFO msg="Listening on 127.0.0.1:11434"
```

**Leave this terminal running.**

---

## Step 4: Run Your App

### **Terminal 2: Start Your Flask App**
```bash
cd ConversationalAI_Prototype
pip install -r requirements.txt
python app.py
```

You should see:
```
✓ Connected to Ollama (mistral)
 * Running on http://127.0.0.1:5000
```

Now responses are **real**, not mocked!

---

## Step 5: Test It

Open http://localhost:5000 in your browser and chat. Watch the personality modes change responses:

**Try this sequence:**

1. **Normal message** (Witty mode):
   ```
   What's something interesting you've learned?
   ```
   → Response will be engaging, humorous

2. **Emotional message** (Empathetic mode):
   ```
   I'm really frustrated with this
   ```
   → Response will be validating, supportive

3. **Question** (Curious mode):
   ```
   How does that work anyway?
   ```
   → Response will explore angles, ask questions back

4. **Sarcasm test** (Sarcasm recovery):
   ```
   Everything I said was sarcasm
   ```
   → Response will reframe prior context

---

## Troubleshooting

### **"Connection refused" error**
- Make sure `ollama serve` is running in another terminal
- Check it's on port 11434

### **"Model not found"**
```bash
ollama pull mistral
```

### **Slow responses**
- Running on CPU? Normal. First inference is slower.
- Use smaller model: `ollama pull neural-chat`
- Or use GPU (Ollama auto-detects NVIDIA/AMD)

### **Out of memory**
- Running a 13B model on 8GB RAM? Use smaller model.
- `ollama pull mistral` (7B, uses ~4GB)
- Close other apps

### **Model too large**
- `llama2` is 7-13GB, takes time to download
- Use `mistral` or `neural-chat` (faster, smaller)

---

## Performance Tips

### **Make Responses Faster**

1. **Use a smaller model**:
   ```bash
   ollama pull neural-chat  # 4GB, fast
   ```
   Then in `app.py`:
   ```python
   ollama = OllamaProvider(model="neural-chat")
   ```

2. **Reduce context length**:
   In `conversation_manager.py`:
   ```python
   context_manager = ContextManager(max_context_turns=3)  # was 5
   ```

3. **Lower temperature** (less creative, faster):
   In `llm_interface.py`:
   ```python
   response = self.generate(prompt, temperature=0.5)  # was 0.8
   ```

### **Improve Response Quality**

1. **Use larger model**:
   ```bash
   ollama pull llama2  # Better quality, slower
   ```

2. **Increase temperature** (more creative):
   ```python
   response = self.generate(prompt, temperature=0.9)
   ```

3. **Better prompts**:
   Edit `_get_personality_instruction()` in `conversation_manager.py`

---

## Running Multiple Models

You can have multiple models installed and switch between them:

```bash
# Install multiple models
ollama pull mistral
ollama pull neural-chat
ollama pull llama2
```

Switch at runtime:
```python
# In app.py
ollama = OllamaProvider(model="llama2")  # change model name
```

---

## Advanced: Deploy with Ollama

### **Option 1: Replit with Ollama**
Ollama runs on Replit but models take time to download. Use smaller model:
```python
ollama = OllamaProvider(model="neural-chat")
```

### **Option 2: Heroku**
Heroku has size limits. Host Ollama separately or use API.

### **Option 3: VPS (DigitalOcean, Linode)**
Full control, can run Ollama freely:
```bash
ssh into_vps
ollama serve &
# Deploy app in separate terminal
python app.py
```

---

## What You Get Now

**Before** (Mock):
```
User: Tell me something interesting
Assistant: [One of 8 pre-written responses]
```

**After** (Real Ollama):
```
User: Tell me something interesting
Assistant: [Genuinely generated response, shaped by current personality mode]
```

Each response is unique, contextual, and actually shaped by the personality system.

---

## Next: Deploy This Live

See `DEPLOY.md` for getting this on the internet so interviewers can test it.

---

## FAQ

**Q: Do I need a GPU?**
A: No. Ollama runs on CPU. GPU makes it 5-10x faster.

**Q: Can I use this in production?**
A: Yes! Ollama is production-ready. Just handle scaling (load balancing, multiple instances).

**Q: How much memory does it use?**
A: 
- Mistral: ~4GB
- Llama2: ~7-13GB (depending on variant)
- Neural-chat: ~4GB

**Q: Can I switch models after starting?**
A: Yes. Just change the model name and restart.

**Q: Does it work offline?**
A: After first download, yes completely offline.

---

## Resources

- **Ollama Website**: https://ollama.ai
- **Model Library**: https://ollama.ai/library
- **GitHub**: https://github.com/jmorganca/ollama
- **Discord Community**: https://discord.gg/ollama

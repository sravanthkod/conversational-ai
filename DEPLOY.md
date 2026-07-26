# Deployment Guide - Live Web Demo

Get your conversational AI running live on the internet in **5 minutes**.

---

## Option 1: Deploy to Replit (Easiest - Recommended)

### Step 1: Push to GitHub
```bash
cd ConversationalAI_Prototype
git add .
git commit -m "Add web UI and Flask backend"
git push origin main
```

### Step 2: Go to Replit
1. Visit [replit.com](https://replit.com)
2. Click **"Import from GitHub"**
3. Paste your repo URL
4. Click **"Create"**

### Step 3: Configure & Run
```bash
# In Replit terminal
pip install -r requirements.txt
python app.py
```

Replit will give you a live URL like: `https://conversational-ai.username.repl.co`

**Done!** Share that link with interviewers. They can interact with it live.

---

## Option 2: Deploy to Heroku (More Professional)

### Step 1: Install Heroku CLI
```bash
# Mac/Linux
brew install heroku

# Windows
# Download from heroku.com/download
```

### Step 2: Login & Deploy
```bash
cd ConversationalAI_Prototype

# Login to Heroku
heroku login

# Create app
heroku create conversational-ai-demo

# Deploy
git push heroku main

# Open in browser
heroku open
```

**Free tier note**: Heroku free dynos sleep after 30 mins. Paid dynos stay awake.

---

## Option 3: Run Locally (For Testing)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run Flask Server
```bash
cd ConversationalAI_Prototype
python app.py
```

### Step 3: Open in Browser
```
http://localhost:5000
```

---

## What the Web UI Shows

### Left Panel (Chat)
- Messages from you and the AI
- Real-time conversation
- Timestamps

### Right Sidebar
- **Personality Mode**: Shows current mode (Witty, Empathetic, Curious, Supportive, Playful)
- **Stats**: Conversation turn count, sarcasm detections
- **Detection Status**: What the system detected
- **Reset**: Start a new conversation
- **Analysis**: See why users drop off at turn 3

---

## Features Demonstrated

1. **Personality Switching**: Mode changes based on user emotion
2. **Sarcasm Detection**: System catches "everything was sarcasm"
3. **Real-time Response**: Instant replies with state updates
4. **Persistent Memory**: Conversation history saved
5. **Emotional Awareness**: Detects frustration, curiosity, need for support
6. **Analysis**: One-click explanation of failure modes

---

## Sharing with Interviewers

1. Deploy to live URL (Replit or Heroku)
2. Send link: `https://conversational-ai-demo.repl.co`
3. They can:
   - Chat with it directly
   - Try sarcasm: "Everything I said was sarcasm"
   - Click "Analysis" to see failure mode explanations
   - See personality modes change in real-time

---

## What to Show in Demo

### Turn 1: Normal Conversation
```
You: What's something interesting you've learned?
Assistant: [Witty response] 🎯
```

### Turn 2: Emotion Detection
```
You: I'm frustrated with this
Assistant: [Empathetic response] 💚
```

### Turn 3: Show Sarcasm Recovery
```
You: Everything I said was sarcasm
Assistant: [Reinterprets all prior context] 🎭
```

### Turn 4: Click Analysis
Show the "Why Users Drop Off" explanation

---

## Troubleshooting

**Error: "ModuleNotFoundError"**
```bash
pip install -r requirements.txt
```

**Error: "Port already in use"**
```bash
# Change port in app.py:
# app.run(port=5001)  # Use different port
```

**Flask not found**
```bash
pip install Flask gunicorn
```

**Replit keeps timing out**
- Switch to paid tier, or
- Use Heroku instead

---

## After Deployment

1. **Test it yourself** - Make sure everything works
2. **Record a 5-minute demo video** showing:
   - The chat interface working
   - Personality mode changes
   - Sarcasm detection
   - Analysis explanation
3. **Create a README** with the live link
4. **Send to interviewers**:
   - "Here's the live demo: [URL]"
   - "And here's the architecture doc: [README]"
   - "Source code is on GitHub: [repo]"

---

## Demo Script

**Show them this sequence:**

1. **Start**: "This is a conversational AI with 5 personality modes"
2. **Normal turn**: Ask about something interesting
3. **Emotion detection**: Say you're frustrated, watch mode change to empathetic
4. **Sarcasm**: Say "everything was sarcasm", watch it reframe
5. **Stats**: Show turn counter, sarcasm detection count
6. **Analysis**: Click "Analysis" to show the failure analysis
7. **Code**: Show them the GitHub repo with architecture docs

---

## What They'll Think

✅ "They built a working demo" (not just theory)
✅ "It's live and interactive" (can test it themselves)
✅ "Shows UI/UX thinking" (not just algorithms)
✅ "Deploys to production" (thinks about ops)
✅ "Can explain failure modes" (systems thinking)

This beats PDF slides by 10x.

---

## Next: Record Demo Video

See `DEMO_VIDEO.md` for script and tips.

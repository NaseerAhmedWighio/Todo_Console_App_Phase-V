# URGENT: API Key Issue

## Problem
Your OpenRouter API key has reached its **USD spending limit**.

Error: `API key USD spend limit exceeded`

This means the free credits on your API key are used up.

## Solution: Get NEW API Key (2 minutes)

### Step 1: Get New Key
1. Visit: https://openrouter.ai/keys
2. Sign in (use different email if needed)
3. Click "Create Key"
4. Copy the new key (starts with `sk-or-v1-`)

### Step 2: Update .env
Edit `backend/.env`:

**Current (NOT WORKING):**
```env
OPENROUTER_API_KEY=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
```

**Replace with YOUR NEW KEY:**
```env
OPENROUTER_API_KEY=sk-or-v1-YOUR-NEW-KEY-HERE
```

### Step 3: Restart Backend
```bash
# Kill existing servers (already done)

# Start backend
cd backend
python main.py
```

### Step 4: Test
```bash
cd D:\Hackathon\todo-app-phase-V
python test_agent_real.py
```

## Alternative: Use Google Gemini (Also FREE)

If you don't want to get a new OpenRouter key:

### Step 1: Get Gemini Key
1. Visit: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

### Step 2: Update .env
```env
API_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-key-here
CHAT_MODEL=google/gemma-3-27b-it:free
```

### Step 3: Restart
```bash
cd backend
python main.py
```

## After Getting New Key

Test with this command:
```bash
python test_agent_real.py
```

Expected output:
```
[OK] Direct API works: Hi!
[OK] Agent created with 10 tools
[OK] Agent response: Hello! How can I help you?
[OK] Response: I've created a task...
```

---

**Current Status:**
- ✅ Agent code is FIXED
- ✅ Configuration is CORRECT
- ❌ API Key is EXHAUSTED (needs replacement)

**Time to fix:** 2 minutes (get new key + update .env)

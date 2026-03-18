# OpenRouter API Key Configuration

## Overview
Your chat agent is using **OpenRouter API** to power the AI chat functionality. The API key is loaded from the environment variable `OPENROUTER_API_KEY`.

## Location of LLM API Usage

### Primary File: `backend/app/services/chat_service.py`

The chat service uses OpenRouter API at these locations:

1. **Line 33-34**: API key and URL initialization
```python
self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
```

2. **Line 147-156**: API request with authentication
```python
headers = {
    "Authorization": f"Bearer {self.openrouter_api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost:3000",
    "X-Title": "Todo App Chat"
}
```

3. **Line 157-163**: HTTP POST to OpenRouter
```python
async with httpx.AsyncClient(timeout=30.0) as client:
    response = await client.post(
        self.openrouter_url,
        headers=headers,
        json=payload
    )
```

## Configuration Files

### 1. `.env` (Production/Local)
**Path**: `backend/.env`

```env
# ===========================================
# LLM API CONFIGURATION (OpenRouter)
# ===========================================
# Get your API key from: https://openrouter.ai/keys
OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
```

### 2. `.env.example` (Template)
**Path**: `backend/.env.example`

```env
# ===========================================
# LLM API CONFIGURATION (OpenRouter)
# ===========================================
# Get your API key from: https://openrouter.ai/keys
OPENROUTER_API_KEY=your-openrouter-api-key-here
```

## Setup Instructions

### 1. Get Your OpenRouter API Key

1. Visit [https://openrouter.ai/keys](https://openrouter.ai/keys)
2. Sign in or create an account
3. Create a new API key
4. Copy the key (starts with `sk-or-v1-`)

### 2. Configure Your Environment

Edit `backend/.env` and replace the placeholder:

```env
OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
```

### 3. Verify Configuration

Run the backend server and test the chat functionality:

```bash
cd backend
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python main.py
```

## Current Model Configuration

The chat service is configured to use:
- **Model**: `arcee-ai/trinity-large-preview:free` (free tier)
- **Max Tokens**: 500 (initial), 300 (follow-up)
- **Temperature**: 0.7

You can change the model in `backend/app/services/chat_service.py` line 141:

```python
payload = {
    "model": "arcee-ai/trinity-large-preview:free",  # Change this
    ...
}
```

### Available Models

Visit [OpenRouter Models](https://openrouter.ai/models) for available models:
- `openai/gpt-3.5-turbo`
- `openai/gpt-4-turbo`
- `anthropic/claude-3-haiku`
- `google/gemini-pro`
- And many more...

## Security Notes

- ✅ The `.env` file is gitignored (not committed to version control)
- ✅ The `.env.example` file contains a placeholder for documentation
- ✅ API key is loaded securely using `os.getenv()`
- ⚠️ Never commit your actual API key to version control
- ⚠️ Rotate your API key if it's ever exposed

## Troubleshooting

### Error: "Invalid API key"
- Check that `OPENROUTER_API_KEY` is set correctly in `backend/.env`
- Ensure there are no extra spaces or quotes around the key
- Verify the key is active on OpenRouter dashboard

### Error: "401 Unauthorized"
- Your API key may be expired or invalid
- Check your OpenRouter account for key status
- Ensure you have sufficient credits

### Error: "429 Rate Limited"
- You've exceeded your rate limit
- Upgrade your OpenRouter plan or wait for the limit to reset

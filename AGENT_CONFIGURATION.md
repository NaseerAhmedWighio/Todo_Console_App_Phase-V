# Agent Configuration & Model Setup

## Overview

Your Todo App uses the **OpenAI Agents SDK** with **OpenRouter API** to power an intelligent chat agent that can manage tasks and tags through natural language conversations.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────┐
│   Frontend  │────▶│  Chat Route  │────▶│ Chat Service│────▶│  Agent   │
│  (Next.js)  │     │  (FastAPI)   │     │             │     │  (SDK)   │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────┘
                                                                  │
                                                                  ▼
                                                           ┌─────────────┐
                                                           │   Tools     │
                                                           │  - CRUD     │
                                                           │  - Tags     │
                                                           └─────────────┘
                                                                  │
                                                                  ▼
                                                           ┌─────────────┐
                                                           │  Database   │
                                                           │  (PostgreSQL)│
                                                           └─────────────┘
```

## Configuration Files

### 1. Environment Variables (`backend/.env`)

```env
# LLM API Configuration
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
API_PROVIDER=openrouter
CHAT_MODEL=meta-llama/llama-3.2-3b-instruct:free
```

### 2. Centralized Config (`backend/agents_sdk/connection.py`)

All model configuration is centralized here:
- Loads from environment variables
- Creates OpenAI client
- Configures model provider
- Exports shared configuration

## Available Models

### Recommended FREE Models (OpenRouter)

| Model | Speed | Quality | Tool Support | Best For |
|-------|-------|---------|--------------|----------|
| `meta-llama/llama-3.2-3b-instruct:free` | ⚡⚡⚡ | ⭐⭐ | ✅ | Fast responses, simple tasks |
| `meta-llama/llama-3.1-8b-instruct:free` | ⚡⚡ | ⭐⭐⭐ | ✅ | Better reasoning |
| `arcee-ai/trinity-mini:free` | ⚡⚡⚡ | ⭐⭐ | ✅ | Quick tool calls |
| `mistralai/mistral-7b-instruct:free` | ⚡⚡ | ⭐⭐⭐ | ✅ | Balanced performance |

### Premium Models (Paid)

| Model | Cost | Quality | Best For |
|-------|------|---------|----------|
| `openai/gpt-4-turbo` | $$$ | ⭐⭐⭐⭐⭐ | Complex reasoning |
| `anthropic/claude-3-opus` | $$$ | ⭐⭐⭐⭐⭐ | Long context |
| `openai/gpt-3.5-turbo` | $ | ⭐⭐⭐⭐ | Production use |

### Google Gemini Models

To use Gemini instead of OpenRouter:

```env
API_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-key
CHAT_MODEL=google/gemma-3-27b-it:free
```

## How to Change Models

### Method 1: Edit `.env` File (Recommended)

1. Open `backend/.env`
2. Change `CHAT_MODEL` value:
   ```env
   CHAT_MODEL=meta-llama/llama-3.1-8b-instruct:free
   ```
3. Restart the backend server

### Method 2: Environment Variable

```bash
# Linux/Mac
export CHAT_MODEL=meta-llama/llama-3.1-8b-instruct:free
python backend/main.py

# Windows PowerShell
$env:CHAT_MODEL="meta-llama/llama-3.1-8b-instruct:free"
python backend/main.py
```

### Method 3: Runtime Override (API)

The chat service accepts model configuration via environment - no code changes needed.

## Agent Capabilities

### Available Tools

1. **create_task** - Create new tasks
   - Title, description, priority, due date, time

2. **list_tasks** - List/filter tasks
   - By status (all/completed/pending)
   - By priority (low/medium/high/urgent)
   - By tag

3. **update_task** - Update existing tasks
   - Any field including completion status

4. **complete_task** - Mark tasks as done

5. **delete_task** - Remove tasks

6. **create_tag** - Create color-coded tags

7. **list_tags** - View all tags

8. **delete_tag** - Remove tags

9. **assign_tag_to_task** - Tag tasks

10. **unassign_tag_from_task** - Remove tags

### Example Conversations

**Create a task:**
```
User: "Create a task to buy groceries tomorrow afternoon with high priority"
Agent: [Calls create_task with parsed parameters]
Response: "I've created a high-priority task 'Buy groceries' for tomorrow afternoon."
```

**Multi-step operation:**
```
User: "Create a task for my meeting and tag it as work"
Agent: 
  1. [Calls create_task]
  2. [Calls create_tag]
  3. [Calls assign_tag_to_task]
Response: "I've created your meeting task and tagged it with 'Work'."
```

## Testing

### Run Comprehensive Test

```bash
cd D:\Hackathon\todo-app-phase-V
python test_agent_full.py
```

This tests:
- Direct tool calls
- Agent with LLM
- All CRUD operations
- Tag management

### Quick Agent Test

```bash
cd backend
python agents_sdk/todo_agent.py
```

Interactive CLI to test natural language commands.

## Troubleshooting

### Agent Not Calling Tools

**Symptom:** Agent responds but doesn't perform actions

**Solution:**
1. Check `AGENTS_SDK_AVAILABLE = True` in `chat_service.py`
2. Verify API key is valid
3. Check model supports tool calling

### API Errors

**Error:** "Invalid API key"
```bash
# Verify .env has correct key
cat backend/.env | grep OPENROUTER
```

**Error:** "Rate limited"
- Wait 60 seconds
- Upgrade OpenRouter plan

### Model Not Loading

**Symptom:** Wrong model being used

**Solution:**
```bash
# Check environment variable
echo $CHAT_MODEL  # Linux/Mac
echo %CHAT_MODEL% # Windows CMD
$env:CHAT_MODEL   # Windows PowerShell
```

### Database Connection Issues

**Symptom:** Tools fail with database errors

**Solution:**
1. Verify `DATABASE_URL` in `.env`
2. Check Neon connection string
3. Run migrations: `python backend/app/database/migrations/verify_schema.py`

## Performance Optimization

### Reduce Latency

1. **Use faster models:**
   ```env
   CHAT_MODEL=arcee-ai/trinity-mini:free
   ```

2. **Reduce context:**
   - Chat service already limits to last 10 messages

3. **Enable caching:**
   - Consider Redis for conversation caching

### Reduce Costs

1. **Use free models** (default configuration)
2. **Limit max_tokens** in agent configuration
3. **Cache common responses**

## Security

### API Key Management

✅ **DO:**
- Store keys in `.env` (gitignored)
- Rotate keys periodically
- Use separate keys for dev/prod

❌ **DON'T:**
- Commit `.env` to git
- Share API keys publicly
- Hardcode keys in source

### Rate Limiting

Chat routes have built-in rate limiting:
- 10 requests/minute per user
- Configurable in `chat_routes.py`

## Monitoring

### Check Agent Status

```python
from agents_sdk.connection import API_PROVIDER, CHAT_MODEL
print(f"Provider: {API_PROVIDER}, Model: {CHAT_MODEL}")
```

### View Logs

```bash
# Backend logs will show:
✓ Agents SDK enabled - Provider: openrouter, Model: meta-llama/llama-3.2-3b-instruct:free
```

## Future Enhancements

- [ ] Add support for more models (Claude, Gemini)
- [ ] Implement conversation summarization
- [ ] Add streaming responses
- [ ] Multi-agent collaboration
- [ ] Custom tool definitions
- [ ] Voice input support

## Support

For issues or questions:
1. Check this documentation
2. Review `test_agent_full.py` for examples
3. Inspect logs for error details
4. Verify environment configuration

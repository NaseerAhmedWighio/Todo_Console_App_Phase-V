# Quick Start - Agent Configuration

## 🚀 3 Steps to Get Started

### 1️⃣ Get Your FREE API Key
```
Visit: https://openrouter.ai/keys
Create account → Generate API key
Copy the key (starts with: sk-or-v1-...)
```

### 2️⃣ Configure Environment
**Edit:** `backend/.env`

```env
OPENROUTER_API_KEY=sk-or-v1-YOUR-ACTUAL-KEY-HERE
API_PROVIDER=openrouter
CHAT_MODEL=meta-llama/llama-3.2-3b-instruct:free
```

### 3️⃣ Install & Run
```bash
# Install dependencies
pip install -r requirements.txt

# Start backend
cd backend
python main.py
```

**Server runs on:** `http://localhost:8001`

---

## 🧪 Test Your Agent

### Quick Test
```bash
python verify_agent_config.py
```

### Full Test Suite
```bash
python test_agent_full.py
```

### Interactive CLI
```bash
cd backend
python agents_sdk/todo_agent.py
```

---

## 🔄 Change Model (Easy!)

**Edit `backend/.env`:**

```env
# Fast & Simple
CHAT_MODEL=arcee-ai/trinity-mini:free

# Better Reasoning  
CHAT_MODEL=meta-llama/llama-3.1-8b-instruct:free

# Most Powerful (Free)
CHAT_MODEL=google/gemma-3-27b-it:free
```

**Then restart backend.**

---

## 💬 Example Usage

### From Frontend (JavaScript)
```javascript
const response = await fetch('http://localhost:8001/api/USER_ID/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_JWT_TOKEN'
  },
  body: JSON.stringify({
    message: "Create a task to call John tomorrow at 3pm"
  })
});

const data = await response.json();
console.log(data.message);
```

### Natural Language Examples
```
User: "Create a task to buy groceries tomorrow afternoon"
→ Agent creates task with due_date="tomorrow", time_str="afternoon"

User: "Show me all my high priority tasks"
→ Agent lists tasks filtered by priority="high"

User: "Mark the groceries task as done"
→ Agent completes the task

User: "Create a work tag and add it to my meeting task"
→ Agent: 1) Creates tag, 2) Finds task, 3) Assigns tag
```

---

## 🛠️ Available Tools

| Tool | What It Does |
|------|--------------|
| `create_task` | Create new tasks |
| `list_tasks` | List/filter tasks |
| `update_task` | Update any field |
| `complete_task` | Mark as done |
| `delete_task` | Remove task |
| `create_tag` | Create color tags |
| `list_tags` | View all tags |
| `delete_tag` | Remove tags |
| `assign_tag_to_task` | Tag tasks |
| `unassign_tag_from_task` | Remove tags |

---

## 📋 Configuration Quick Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | Required | Your API key |
| `API_PROVIDER` | `openrouter` | Provider name |
| `CHAT_MODEL` | `llama-3.2-3b-instruct:free` | AI model |
| `DATABASE_URL` | Required | PostgreSQL connection |
| `JWT_SECRET` | Required | Authentication secret |

---

## 🐛 Common Issues

### "API key not set"
→ Edit `backend/.env` and add your key

### "Module not found"
→ Run: `pip install -r requirements.txt`

### "Database connection failed"
→ Check `DATABASE_URL` in `.env`

### Agent not calling tools
→ Verify `AGENTS_SDK_AVAILABLE = True` in logs

---

## 📚 Full Documentation

- `AGENT_FIX_SUMMARY.md` - What was fixed
- `AGENT_CONFIGURATION.md` - Complete guide
- `README.md` - Project overview

---

## ✅ Verification Checklist

- [ ] API key in `backend/.env`
- [ ] Dependencies installed
- [ ] Backend starts without errors
- [ ] Logs show: "✓ Agents SDK enabled"
- [ ] Test script passes
- [ ] Can create tasks via chat

---

**🎉 You're ready to go!**

Your agent can now:
- ✅ Understand natural language
- ✅ Call tools to manage tasks
- ✅ Work with tags
- ✅ Handle multi-step operations
- ✅ Store everything in database

**Happy coding!** 🚀

# 🔍 Debugging Tomorrow +2 Days Issue

## Status: Debug Logging Added

I've added comprehensive debug logging to trace exactly where the date is being modified.

---

## Debug Logs You'll See

When you send: `"Create a task to buy groceries tomorrow"`

### Expected Logs:
```
[NLP] Input: Create a task to buy groceries tomorrow
[NLP] Output: title='Buy Groceries', due_date='2026-03-03', time_str='None', tag='None'
[DEBUG] MCP create_task: ISO date detected: 2026-03-03, parsed to: 2026-03-03 12:00:00
[INFO] create_task: title='Buy Groceries', user_id='xxx', due_date='2026-03-03', ...
```

### If Using Agent SDK:
```
[INFO] run_agent_with_user_message: user_id='xxx', global_user_id='xxx'
[INFO] Processing message: Create a task to buy groceries tomorrow...
[DEBUG] create_task: Processing due_date='2026-03-03'
[DEBUG] create_task: ISO date parsed: 2026-03-03 12:00:00
```

---

## How to Check

1. **Send your request** with "tomorrow" in the frontend
2. **Check backend console** for the debug logs
3. **Share the logs** with me so I can identify the issue

---

## Possible Causes

### 1. Agent Model Misinterpretation
The AI model (stepfun/step-3.5-flash:free) might be:
- Not using the NLP parser
- Parsing "tomorrow" incorrectly itself
- Adding its own date logic

**Solution:** Switch to a better model or force NLP parsing

### 2. Double Parsing
Date might be parsed twice:
- Once by NLP parser (correct: +1 day)
- Again by agent or MCP server (adding more days)

**Solution:** Already fixed - ISO dates are now used directly

### 3. Timezone Issues
Date might be shifted by timezone conversion

**Solution:** Set time to noon (12:00) to avoid midnight rollover

---

## Files with Debug Logging

| File | Debug Added |
|------|-------------|
| `app/services/natural_language_parser.py` | Shows input/output of NLP parsing |
| `app/services/mcp_server.py` | Shows date parsing in create_task_tool |
| `agents_sdk/todo_agent.py` | Shows date parsing in create_task |

---

## Test Commands

### Test 1: Simple Tomorrow
```
"Create a task to test tomorrow"
```

### Test 2: Tomorrow with Time
```
"Create a task to test tomorrow morning"
```

### Test 3: Tomorrow with Tag
```
"Create a task to test tomorrow with work tag"
```

---

## Next Steps

1. **Test with your frontend**
2. **Copy the backend console output**
3. **Share it with me** so I can pinpoint the exact issue

---

## Quick Fix (If Agent is the Problem)

If the logs show the agent is not using NLP parsing, we can:

### Option A: Force Direct Tool Execution
Modify `chat_service.py` to always use direct MCP tools instead of agent SDK

### Option B: Better Model
Use a more reliable model:
```env
CHAT_MODEL=meta-llama/llama-3.2-3b-instruct:free
```

### Option C: Enhanced Agent Instructions
Update agent instructions to always use NLP parser for dates

---

**Server is running with debug logging enabled!** 🚀

Test now and share the logs!

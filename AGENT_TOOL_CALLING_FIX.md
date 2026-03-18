# Chatbot Agent Tool Calling Fix Summary

## Overview
Fixed the chatbot agent to properly support all CRUD operations (Create, Read, Update, Delete) for tasks and tags with configurable model support.

## Changes Made

### 1. Environment Configuration (`.env`)
Created a configurable environment file to switch between different AI models:

```env
# OpenRouter API Key (for multiple model access)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Gemini API Key (alternative)
GEMINI_API_KEY=your_gemini_api_key_here

# Model Configuration
CHAT_MODEL=gemini-2.0-flash

# API Provider: 'gemini' or 'openrouter'
API_PROVIDER=gemini
```

**Supported Models:**
- `gemini-2.0-flash` (via Gemini API)
- `arcee-ai/trinity-mini:free` (via OpenRouter - free)
- `google/gemini-2.0-flash-001:free` (via OpenRouter - free)
- `meta-llama/llama-3.2-90b-vision-instruct:free` (via OpenRouter - free)

### 2. Fixed `todo_agent.py`
Completely rewrote the agent with proper tool calling support:

**Key Features:**
- ✅ Configurable model via environment variables
- ✅ Proper `@function_tool` decorators for all tools
- ✅ All CRUD operations supported
- ✅ Automatic user_id injection
- ✅ Proper error handling with error codes

**Available Tools:**
1. `create_task` - Create tasks with title, description, priority, due date, time
2. `list_tasks` - List tasks with filters (status, priority, tags)
3. `update_task` - Update task title, description, priority, due date, completion status
4. `complete_task` - Mark task as completed
5. `delete_task` - Delete a task permanently
6. `create_tag` - Create a tag with name and color
7. `list_tags` - List all tags
8. `delete_tag` - Delete a tag (removes from all tasks)
9. `assign_tag_to_task` - Assign a tag to a task
10. `unassign_tag_from_task` - Remove a tag from a task

### 3. Updated `chat_service.py`
Simplified to use the agent SDK directly:

```python
async def _process_with_agents_sdk(...):
    model = os.getenv("CHAT_MODEL", model_name)
    return await run_agent_with_user_message(
        user_id=user_id,
        user_message=user_message,
        conversation_history=conversation_history,
        model=model
    )
```

### 4. Updated `mcp_server.py`
Added missing `unassign_tag_from_task_tool` method and updated tools spec.

## How to Use

### Option 1: Direct Tool Calling (Recommended for Testing)
```python
from backend.agents_sdk.todo_agent import (
    set_current_user_id,
    create_task,
    update_task,
    delete_task,
    create_tag,
    assign_tag_to_task
)

# Set user ID
set_current_user_id("your-user-uuid")

# Create a task
result = create_task(
    title="Buy groceries",
    description="Milk, eggs, bread",
    priority="high",
    due_date="tomorrow",
    time_str="morning"
)

# Update the task
update_task(
    task_id=result['data']['id'],
    title="Buy groceries and vegetables",
    priority="urgent"
)

# Create and assign a tag
tag_result = create_tag(name="Shopping", color="#FF0000")
assign_tag_to_task(task_id=result['data']['id'], tag_id=tag_result['data']['id'])
```

### Option 2: Natural Language with Agent
```python
from backend.agents_sdk.todo_agent import run_agent_sync, set_current_user_id

set_current_user_id("your-user-uuid")

# Create a task with natural language
response = run_agent_sync(
    "Create a high priority task to finish the report due tomorrow morning",
    "your-user-uuid"
)

# Update a task
response = run_agent_sync(
    "Update the first task to add description 'urgent deadline'",
    "your-user-uuid"
)

# Delete a task
response = run_agent_sync(
    "Delete the first task",
    "your-user-uuid"
)
```

### Option 3: Via Chat API
Send messages to the chat endpoint:
```
POST /api/{user_id}/chat
{
    "message": "Create a task to call John tomorrow at 3pm",
    "conversation_id": "optional-conversation-id"
}
```

## Model Configuration

### Using Gemini API
```env
API_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
CHAT_MODEL=gemini-2.0-flash
```

### Using OpenRouter (Multiple Free Models)
```env
API_PROVIDER=openrouter
OPENROUTER_API_KEY=your_openrouter_api_key
CHAT_MODEL=arcee-ai/trinity-mini:free
```

**Free Models on OpenRouter:**
- `arcee-ai/trinity-mini:free` - Fast, good for tool calling
- `google/gemini-2.0-flash-001:free` - Google's Gemini 2.0 Flash
- `meta-llama/llama-3.2-90b-vision-instruct:free` - Meta's Llama 3.2

## Testing

Run the test script:
```bash
cd D:\Hackathon\todo-app-phase-V
python test_agent_tools.py
```

Or test individual tools:
```bash
cd D:\Hackathon\todo-app-phase-V\backend
python -m agents_sdk.todo_agent
```

## MCP Server Note

**The MCP (Model Context Protocol) server is NOT required** for this implementation. The agent uses the OpenAI Agents SDK directly with `@function_tool` decorators, which provides native tool calling support.

If you want to use an MCP server, you would need to:
1. Install the MCP SDK: `pip install mcp`
2. Set up an MCP server with your tools
3. Connect the agent to the MCP server

However, the current implementation is simpler and works directly with the Agents SDK.

## Troubleshooting

### Tool Not Being Called
1. Check that the model supports function calling (Gemini 2.0 and most modern models do)
2. Verify the tool is in the agent's `tools` list
3. Check the agent instructions mention the tool

### Model Connection Error
1. Verify API key is set in `.env`
2. Check API provider matches your key type
3. Test with a different model

### User ID Error
Make sure to set the user ID before calling tools:
```python
set_current_user_id("your-valid-uuid")
```

## Example: Complete Workflow

```python
from backend.agents_sdk.todo_agent import run_agent_sync, set_current_user_id

# Set user ID
set_current_user_id("550e8400-e29b-41d4-a716-446655440000")

# 1. Create a task
response = run_agent_sync(
    "Create a high priority task to finish project report due tomorrow at 2pm",
    "550e8400-e29b-41d4-a716-446655440000"
)
print(response)

# 2. Create a tag
response = run_agent_sync(
    "Create a tag called 'Work' with blue color",
    "550e8400-e29b-41d4-a716-446655440000"
)
print(response)

# 3. Assign tag to task
response = run_agent_sync(
    "Assign the Work tag to the project report task",
    "550e8400-e29b-41d4-a716-446655440000"
)
print(response)

# 4. List all tasks
response = run_agent_sync(
    "Show me all my tasks",
    "550e8400-e29b-41d4-a716-446655440000"
)
print(response)

# 5. Update task
response = run_agent_sync(
    "Update the project report task to add description 'Q1 financial report'",
    "550e8400-e29b-41d4-a716-446655440000"
)
print(response)

# 6. Mark as completed
response = run_agent_sync(
    "Mark the project report task as completed",
    "550e8400-e29b-41d4-a716-446655440000"
)
print(response)

# 7. Delete task
response = run_agent_sync(
    "Delete the project report task",
    "550e8400-e29b-41d4-a716-446655440000"
)
print(response)

# 8. Delete tag
response = run_agent_sync(
    "Delete the Work tag",
    "550e8400-e29b-41d4-a716-446655440000"
)
print(response)
```

## Summary

✅ All CRUD operations now work:
- Create tasks and tags
- Read/list tasks and tags with filters
- Update tasks (title, description, priority, due date, completion)
- Delete tasks and tags
- Assign/unassign tags to/from tasks

✅ Model is configurable via environment variables

✅ Works with any model that supports function calling:
- Gemini 2.0 Flash
- OpenRouter models
- Any OpenAI-compatible model

✅ No MCP server required - uses OpenAI Agents SDK directly

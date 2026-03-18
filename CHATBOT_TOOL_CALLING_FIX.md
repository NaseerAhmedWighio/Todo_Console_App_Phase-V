# Chatbot Tool Calling Fix

## Problem
The chatbot was responding with "I received an unexpected response" when users asked it to create tasks with tags (e.g., "Create a task to Go to Governor House at afternoon with high priority and add tag of work").

## Root Cause
The issue was with how the chat service was handling tool calling with the AI model. The `arcee-ai/trinity-mini:free` model supports tool/function calling, but the implementation wasn't properly:
1. Extracting tool calls from the model response
2. Executing the tools with the correct parameters
3. Sending tool results back to the model for final response generation

## Solution

### 1. Created OpenAI Agents SDK Integration (`backend/agents_sdk/todo_agent.py`)
- Implemented all todo operations as `@function_tool` decorated functions:
  - `create_task` - Create tasks with title, description, priority, due date, and time
  - `list_tasks` - List tasks with filters
  - `update_task` - Update task properties
  - `complete_task` - Mark tasks as completed
  - `delete_task` - Delete tasks
  - `create_tag` - Create tags with name and color
  - `list_tags` - List all tags
  - `assign_tag_to_task` - Assign tags to tasks

- Added automatic user_id injection via global context
- Created comprehensive agent instructions for multi-step operations

### 2. Updated Chat Service (`backend/app/services/chat_service.py`)
- Implemented manual tool calling loop in `_process_with_agents_sdk()`:
  1. **First API call**: Send user message with tools spec, get tool calls
  2. **Execute tools**: Run each tool with auto-injected user_id
  3. **Second API call**: Send tool results back, get final natural language response

- Added fallback to legacy API if Agents SDK fails
- Proper error handling and logging

### 3. Fixed Import Paths
- Renamed `backend/agents-sdk` to `backend/agents_sdk` (Python-compatible naming)
- Updated all imports to use correct paths

### 4. Model Configuration (`backend/agents_sdk/connection.py`)
- Using `arcee-ai/trinity-mini:free` which supports tool calling
- Configured OpenRouter API integration

## How It Works

### Example Flow: "Create a task to Go to Governor House at afternoon with high priority and add tag of work"

1. **User sends message** → Chat service receives request

2. **First API call**:
   ```json
   {
     "model": "arcee-ai/trinity-mini:free",
     "messages": [system, user_message],
     "tools": [create_task, create_tag, assign_tag_to_task, ...],
     "tool_choice": "auto"
   }
   ```

3. **Model responds with tool calls**:
   ```json
   {
     "tool_calls": [
       {"function": {"name": "create_task", "arguments": {"title": "Go to Governor House", "priority": "high", "due_date": "tomorrow", "time_str": "afternoon"}}},
       {"function": {"name": "create_tag", "arguments": {"name": "work", "color": "#FF0000"}}},
       {"function": {"name": "assign_tag_to_task", "arguments": {"task_id": "...", "tag_id": "..."}}}
     ]
   }
   ```

4. **Chat service executes tools**:
   - Calls `create_task()` → returns task_id
   - Calls `create_tag()` → returns tag_id
   - Calls `assign_tag_to_task(task_id, tag_id)` → assigns tag

5. **Second API call** (with tool results):
   ```json
   {
     "messages": [system, user_message, assistant_tool_calls, tool_results],
     "tool_choice": "none"
   }
   ```

6. **Model generates final response**:
   "I've created the task 'Go to Governor House' for tomorrow afternoon with high priority and assigned the 'work' tag to it."

## Testing

Run the test script to verify:
```bash
cd backend
python test_agents_sdk.py
```

## Files Changed

1. `backend/agents_sdk/todo_agent.py` - New file with agent and tools
2. `backend/agents_sdk/connection.py` - Updated model configuration
3. `backend/app/services/chat_service.py` - Updated with manual tool calling loop
4. `backend/test_agents_sdk.py` - Test script

## Benefits

- ✅ Proper tool calling with correct parameter extraction
- ✅ Automatic user_id injection for all operations
- ✅ Multi-step operations (create task + tag + assign) work correctly
- ✅ Natural language responses after tool execution
- ✅ Fallback to legacy API if tools fail
- ✅ Comprehensive logging for debugging

## Next Steps

The chatbot should now properly handle:
- Task creation with natural language dates/times
- Tag creation and assignment
- Multi-step operations
- All existing todo operations (list, update, complete, delete)

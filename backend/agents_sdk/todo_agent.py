"""
Enhanced Todo Agent using OpenAI Agents SDK with @function_tool decorators.
Supports all CRUD operations: Create, Read, Update, Delete for tasks and tags.
Configurable model via environment variables.
"""
from agents import (
    Agent, Runner, function_tool,
    ModelSettings
)
from dotenv import find_dotenv, load_dotenv
from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime
import json
from sqlmodel import Session, select

# Load environment variables
load_dotenv(find_dotenv())

# Import from app module
try:
    from app.models.todo import Todo
    from app.models.tag import Tag
    from app.models.task_tag import TaskTag
    from app.database.session import engine
    from app.services.mcp_server import MCPServer
except ImportError:
    from backend.app.models.todo import Todo
    from backend.app.models.tag import Tag
    from backend.app.models.task_tag import TaskTag
    from backend.app.database.session import engine
    from backend.app.services.mcp_server import MCPServer

# ============ CONFIGURATION ============
# Import configuration from connection module (centralized config)
# This sets up the OpenRouter client as the default
try:
    from agents_sdk.connection import CHAT_MODEL, API_PROVIDER
except ImportError:
    from connection import CHAT_MODEL, API_PROVIDER

# Use model name from connection config
model_name = CHAT_MODEL

# ============ GLOBAL STATE ============
_current_user_id: Optional[str] = None


def set_current_user_id(user_id: str):
    """Set the current user ID for all tools"""
    global _current_user_id
    _current_user_id = user_id


def get_current_user_id() -> Optional[str]:
    """Get the current user ID"""
    return _current_user_id


# ============ TAG TOOLS ============

@function_tool
def create_tag(name: str, color: str = "#3B82F6", user_id: str = None) -> Dict[str, Any]:
    """
    Create a new tag with name and color.
    
    Args:
        name: Tag name (required)
        color: Hex color code (default: #3B82F6)
        user_id: User ID (auto-injected)
    
    Returns:
        Success status and tag data
    """
    try:
        if not user_id:
            user_id = get_current_user_id()
        
        if not user_id:
            return {"success": False, "message": "User ID required. Please login first.", "error_code": "AUTH_REQUIRED"}
        
        user_uuid = uuid.UUID(user_id)
        
        with Session(engine) as db_session:
            existing = db_session.exec(
                select(Tag).where((Tag.name == name) & (Tag.user_id == user_uuid))
            ).first()
            
            if existing:
                return {"success": False, "message": f"Tag '{name}' already exists", "error_code": "DUPLICATE"}
            
            new_tag = Tag(name=name, color=color, user_id=user_uuid)
            db_session.add(new_tag)
            db_session.commit()
            db_session.refresh(new_tag)
            
            return {
                "success": True,
                "message": f"Tag '{name}' created successfully",
                "data": {
                    "id": str(new_tag.id),
                    "name": new_tag.name,
                    "color": new_tag.color
                }
            }
    except ValueError:
        return {"success": False, "message": "Invalid user ID format", "error_code": "INVALID_ID"}
    except Exception as e:
        return {"success": False, "message": f"Failed to create tag: {str(e)}", "error_code": "CREATE_FAILED"}


@function_tool
def list_tags(user_id: str = None) -> Dict[str, Any]:
    """
    List all tags for a user.
    
    Args:
        user_id: User ID (auto-injected)
    
    Returns:
        List of tags
    """
    try:
        if not user_id:
            user_id = get_current_user_id()
        
        if not user_id:
            return {"success": False, "message": "User ID required", "error_code": "AUTH_REQUIRED"}
        
        user_uuid = uuid.UUID(user_id)
        
        with Session(engine) as db_session:
            tags = db_session.exec(
                select(Tag).where(Tag.user_id == user_uuid).order_by(Tag.name)
            ).all()
            
            return {
                "success": True,
                "message": f"Found {len(tags)} tags",
                "data": [
                    {"id": str(tag.id), "name": tag.name, "color": tag.color}
                    for tag in tags
                ]
            }
    except Exception as e:
        return {"success": False, "message": f"Failed to list tags: {str(e)}", "error_code": "LIST_FAILED"}


@function_tool
def delete_tag(tag_id: str, user_id: str = None) -> Dict[str, Any]:
    """
    Delete a tag permanently. This will also remove the tag from all tasks.
    
    Args:
        tag_id: Tag ID to delete (required)
        user_id: User ID (auto-injected)
    
    Returns:
        Success status
    """
    try:
        if not user_id:
            user_id = get_current_user_id()
        
        if not user_id:
            return {"success": False, "message": "User ID required", "error_code": "AUTH_REQUIRED"}
        
        user_uuid = uuid.UUID(user_id)
        tag_uuid = uuid.UUID(tag_id)
        
        with Session(engine) as db_session:
            tag = db_session.get(Tag, tag_uuid)
            
            if not tag:
                return {"success": False, "message": "Tag not found", "error_code": "NOT_FOUND"}
            
            if tag.user_id != user_uuid:
                return {"success": False, "message": "Access denied: You can only delete your own tags", "error_code": "ACCESS_DENIED"}
            
            tag_name = tag.name
            
            # Delete all task-tag assignments
            assignments = db_session.exec(select(TaskTag).where(TaskTag.tag_id == tag_uuid)).all()
            for assignment in assignments:
                db_session.delete(assignment)
            
            db_session.delete(tag)
            db_session.commit()
            
            return {
                "success": True,
                "message": f"Tag '{tag_name}' deleted successfully",
                "data": {"id": str(tag_id)}
            }
    except ValueError:
        return {"success": False, "message": "Invalid ID format", "error_code": "INVALID_ID"}
    except Exception as e:
        return {"success": False, "message": f"Failed to delete tag: {str(e)}", "error_code": "DELETE_FAILED"}


@function_tool
def assign_tag_to_task(task_id: str, tag_id: str, user_id: str = None) -> Dict[str, Any]:
    """
    Assign a tag to a task.
    
    Args:
        task_id: Task ID to assign tag to
        tag_id: Tag ID to assign
        user_id: User ID (auto-injected)
    
    Returns:
        Success status
    """
    try:
        if not user_id:
            user_id = get_current_user_id()
        
        if not user_id:
            return {"success": False, "message": "User ID required", "error_code": "AUTH_REQUIRED"}
        
        user_uuid = uuid.UUID(user_id)
        task_uuid = uuid.UUID(task_id)
        tag_uuid = uuid.UUID(tag_id)
        
        with Session(engine) as db_session:
            task = db_session.get(Todo, task_uuid)
            if not task or task.user_id != user_uuid:
                return {"success": False, "message": "Task not found", "error_code": "NOT_FOUND"}
            
            tag = db_session.get(Tag, tag_uuid)
            if not tag or tag.user_id != user_uuid:
                return {"success": False, "message": "Tag not found", "error_code": "NOT_FOUND"}
            
            existing = db_session.exec(
                select(TaskTag).where((TaskTag.task_id == task_uuid) & (TaskTag.tag_id == tag_uuid))
            ).first()
            
            if existing:
                return {"success": True, "message": "Tag already assigned to task", "error_code": "ALREADY_ASSIGNED"}
            
            assignment = TaskTag(task_id=task_uuid, tag_id=tag_uuid)
            db_session.add(assignment)
            db_session.commit()
            
            return {
                "success": True,
                "message": f"Tag '{tag.name}' assigned to task '{task.title}'",
                "data": {"task_id": str(task_id), "tag_id": str(tag_id)}
            }
    except ValueError:
        return {"success": False, "message": "Invalid ID format", "error_code": "INVALID_ID"}
    except Exception as e:
        return {"success": False, "message": f"Failed to assign tag: {str(e)}", "error_code": "ASSIGN_FAILED"}


@function_tool
def unassign_tag_from_task(task_id: str, tag_id: str, user_id: str = None) -> Dict[str, Any]:
    """
    Remove a tag from a task.
    
    Args:
        task_id: Task ID to remove tag from
        tag_id: Tag ID to remove
        user_id: User ID (auto-injected)
    
    Returns:
        Success status
    """
    try:
        if not user_id:
            user_id = get_current_user_id()
        
        if not user_id:
            return {"success": False, "message": "User ID required", "error_code": "AUTH_REQUIRED"}
        
        user_uuid = uuid.UUID(user_id)
        task_uuid = uuid.UUID(task_id)
        tag_uuid = uuid.UUID(tag_id)
        
        with Session(engine) as db_session:
            assignment = db_session.exec(
                select(TaskTag).where((TaskTag.task_id == task_uuid) & (TaskTag.tag_id == tag_uuid))
            ).first()
            
            if not assignment:
                return {"success": False, "message": "Tag assignment not found", "error_code": "NOT_FOUND"}
            
            task = db_session.get(Todo, task_uuid)
            if not task or task.user_id != user_uuid:
                return {"success": False, "message": "Access denied", "error_code": "ACCESS_DENIED"}
            
            db_session.delete(assignment)
            db_session.commit()
            
            return {
                "success": True,
                "message": "Tag removed from task successfully",
                "data": {"task_id": str(task_id), "tag_id": str(tag_id)}
            }
    except ValueError:
        return {"success": False, "message": "Invalid ID format", "error_code": "INVALID_ID"}
    except Exception as e:
        return {"success": False, "message": f"Failed to unassign tag: {str(e)}", "error_code": "UNASSIGN_FAILED"}


# ============ TASK TOOLS ============

@function_tool
def create_task(
    title: str,
    description: Optional[str] = None,
    priority: Optional[str] = "medium",
    due_date: Optional[str] = None,
    time_str: Optional[str] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new task with title, description, priority, and due date.

    Args:
        title: Task title (required)
        description: Task description (optional)
        priority: Task priority - low/medium/high/urgent (default: medium)
        due_date: Due date in natural language (e.g., "tomorrow", "next Monday", "in 2 days")
        time_str: Time specification (e.g., "morning", "afternoon", "9pm", "2:30 PM")
        user_id: User ID (auto-injected from global state if not provided)

    Returns:
        Success status and task data
    """
    try:
        # First try to use provided user_id, then fall back to global state
        effective_user_id = user_id or get_current_user_id()

        if not effective_user_id:
            print("[ERROR] create_task: No user_id provided and no global user_id set")
            return {"success": False, "message": "User ID required. Please login first.", "error_code": "AUTH_REQUIRED"}

        # Debug logging
        print(f"[INFO] create_task: title='{title}', user_id='{effective_user_id}', due_date='{due_date}', time_str='{time_str}', priority='{priority}'")
        
        # Parse due_date if it's a relative date string
        due_datetime = None
        if due_date:
            print(f"[DEBUG] create_task: Processing due_date='{due_date}'")
            # Check if due_date is already an ISO date (YYYY-MM-DD)
            import re
            if re.match(r'^\d{4}-\d{2}-\d{2}$', due_date):
                # It's already parsed by NLP, use it directly
                try:
                    due_datetime = datetime.strptime(due_date, '%Y-%m-%d')
                    due_datetime = due_datetime.replace(hour=12, minute=0, second=0)
                    print(f"[DEBUG] create_task: ISO date parsed: {due_datetime}")
                except Exception as e:
                    print(f"[DEBUG] create_task: Failed to parse ISO date: {e}")
            else:
                # Use MCP parser for relative dates
                mcp = MCPServer(None)
                due_datetime = mcp.parse_natural_language_datetime(due_date, time_str)
                print(f"[DEBUG] create_task: NLP parsed: {due_datetime}")

        # Convert user_id to UUID
        import uuid
        user_uuid = uuid.UUID(effective_user_id)

        with Session(engine) as db_session:
            new_task = Todo(
                title=title,
                description=description or "",
                priority=priority or "medium",
                due_date=due_datetime,
                is_completed=False,
                user_id=user_uuid
            )

            db_session.add(new_task)
            db_session.commit()
            db_session.refresh(new_task)

            return {
                "success": True,
                "message": f"Task '{title}' created successfully",
                "data": {
                    "id": str(new_task.id),
                    "title": new_task.title,
                    "description": new_task.description,
                    "priority": new_task.priority,
                    "due_date": new_task.due_date.isoformat() if new_task.due_date else None,
                    "completed": new_task.is_completed
                }
            }
    except ValueError as e:
        print(f"[ERROR] create_task: Invalid user ID format - {e}")
        return {"success": False, "message": "Invalid user ID format", "error_code": "INVALID_ID"}
    except Exception as e:
        print(f"[ERROR] create_task: Failed to create task - {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "message": f"Failed to create task: {str(e)}", "error_code": "CREATE_FAILED"}


@function_tool
def list_tasks(
    status: Optional[str] = "all",
    priority: Optional[str] = None,
    tag_id: Optional[str] = None,
    limit: int = 50,
    user_id: str = None
) -> Dict[str, Any]:
    """
    List tasks with optional filters.
    
    Args:
        status: Filter by status - all/completed/pending (default: all)
        priority: Filter by priority - low/medium/high/urgent
        tag_id: Filter by tag ID
        limit: Maximum results (default: 50)
        user_id: User ID (auto-injected)
    
    Returns:
        List of tasks
    """
    try:
        if not user_id:
            user_id = get_current_user_id()
        
        if not user_id:
            return {"success": False, "message": "User ID required", "error_code": "AUTH_REQUIRED"}
        
        user_uuid = uuid.UUID(user_id)
        
        with Session(engine) as db_session:
            statement = select(Todo).where(Todo.user_id == user_uuid)
            
            if status == "completed":
                statement = statement.where(Todo.is_completed == True)
            elif status == "pending":
                statement = statement.where(Todo.is_completed == False)
            
            if priority:
                statement = statement.where(Todo.priority == priority)
            
            if tag_id:
                tag_uuid = uuid.UUID(tag_id)
                tag_statement = select(TaskTag.task_id).where(TaskTag.tag_id == tag_uuid)
                statement = statement.where(Todo.id.in_(tag_statement))
            
            statement = statement.order_by(Todo.created_at.desc()).limit(limit)
            tasks = db_session.exec(statement).all()
            
            return {
                "success": True,
                "message": f"Found {len(tasks)} tasks",
                "data": [
                    {
                        "id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "priority": task.priority,
                        "due_date": task.due_date.isoformat() if task.due_date else None,
                        "completed": task.is_completed,
                        "tags": [
                            {"id": str(t.tag.id), "name": t.tag.name, "color": t.tag.color}
                            for t in task.tags
                        ] if hasattr(task, 'tags') else []
                    }
                    for task in tasks
                ]
            }
    except Exception as e:
        return {"success": False, "message": f"Failed to list tasks: {str(e)}", "error_code": "LIST_FAILED"}


@function_tool
def update_task(
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    time_str: Optional[str] = None,
    completed: Optional[bool] = None,
    user_id: str = None
) -> Dict[str, Any]:
    """
    Update an existing task.
    
    Args:
        task_id: Task ID to update (required)
        title: New title
        description: New description
        priority: New priority - low/medium/high/urgent
        due_date: New due date in natural language
        time_str: Time specification for due date
        completed: Completion status (true/false)
        user_id: User ID (auto-injected)
    
    Returns:
        Success status and updated task data
    """
    try:
        if not user_id:
            user_id = get_current_user_id()
        
        if not user_id:
            return {"success": False, "message": "User ID required", "error_code": "AUTH_REQUIRED"}
        
        user_uuid = uuid.UUID(user_id)
        task_uuid = uuid.UUID(task_id)
        
        with Session(engine) as db_session:
            task = db_session.get(Todo, task_uuid)
            
            if not task or task.user_id != user_uuid:
                return {"success": False, "message": "Task not found", "error_code": "NOT_FOUND"}
            
            # Update fields
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if priority is not None:
                task.priority = priority
            if completed is not None:
                task.is_completed = completed
            if due_date is not None:
                mcp = MCPServer(None)
                task.due_date = mcp.parse_natural_language_datetime(due_date, time_str)
            
            db_session.add(task)
            db_session.commit()
            db_session.refresh(task)
            
            return {
                "success": True,
                "message": f"Task '{task.title}' updated successfully",
                "data": {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "completed": task.is_completed
                }
            }
    except ValueError:
        return {"success": False, "message": "Invalid ID format", "error_code": "INVALID_ID"}
    except Exception as e:
        return {"success": False, "message": f"Failed to update task: {str(e)}", "error_code": "UPDATE_FAILED"}


@function_tool
def complete_task(task_id: str, user_id: str = None) -> Dict[str, Any]:
    """
    Mark a task as completed.
    
    Args:
        task_id: Task ID to complete (required)
        user_id: User ID (auto-injected)
    
    Returns:
        Success status
    """
    try:
        if not user_id:
            user_id = get_current_user_id()
        
        if not user_id:
            return {"success": False, "message": "User ID required", "error_code": "AUTH_REQUIRED"}
        
        user_uuid = uuid.UUID(user_id)
        task_uuid = uuid.UUID(task_id)
        
        with Session(engine) as db_session:
            task = db_session.get(Todo, task_uuid)
            
            if not task or task.user_id != user_uuid:
                return {"success": False, "message": "Task not found", "error_code": "NOT_FOUND"}
            
            task.is_completed = True
            db_session.add(task)
            db_session.commit()
            
            return {
                "success": True,
                "message": f"Task '{task.title}' marked as completed",
                "data": {"id": str(task.id), "title": task.title, "completed": True}
            }
    except ValueError:
        return {"success": False, "message": "Invalid ID format", "error_code": "INVALID_ID"}
    except Exception as e:
        return {"success": False, "message": f"Failed to complete task: {str(e)}", "error_code": "COMPLETE_FAILED"}


@function_tool
def delete_task(task_id: str, user_id: str = None) -> Dict[str, Any]:
    """
    Delete a task permanently.
    
    Args:
        task_id: Task ID to delete (required)
        user_id: User ID (auto-injected)
    
    Returns:
        Success status
    """
    try:
        if not user_id:
            user_id = get_current_user_id()
        
        if not user_id:
            return {"success": False, "message": "User ID required", "error_code": "AUTH_REQUIRED"}
        
        user_uuid = uuid.UUID(user_id)
        task_uuid = uuid.UUID(task_id)
        
        with Session(engine) as db_session:
            task = db_session.get(Todo, task_uuid)
            
            if not task or task.user_id != user_uuid:
                return {"success": False, "message": "Task not found", "error_code": "NOT_FOUND"}
            
            task_title = task.title
            db_session.delete(task)
            db_session.commit()
            
            return {
                "success": True,
                "message": f"Task '{task_title}' deleted successfully",
                "data": {"id": str(task_id)}
            }
    except ValueError:
        return {"success": False, "message": "Invalid ID format", "error_code": "INVALID_ID"}
    except Exception as e:
        return {"success": False, "message": f"Failed to delete task: {str(e)}", "error_code": "DELETE_FAILED"}


# ============ AGENT DEFINITION ============

def create_todo_agent(model: str = None) -> Agent:
    """
    Create a comprehensive todo agent with all tools.
    Uses the default model from connection.py configuration.
    """
    return _create_agent_with_model(model_name if model is None else model)


def create_todo_agent_with_model(model: str) -> Agent:
    """
    Create a comprehensive todo agent with a specific model.
    
    Args:
        model: The model name to use (e.g., 'meta-llama/llama-3.2-3b-instruct:free')
    """
    return _create_agent_with_model(model)


def _create_agent_with_model(model: str) -> Agent:
    """
    Internal function to create agent with model configuration.
    
    The model parameter accepts OpenRouter model names like:
    - meta-llama/llama-3.2-3b-instruct:free
    - meta-llama/llama-3.1-8b-instruct:free
    - etc.
    
    Since the Agents SDK doesn't support these prefixes directly,
    we use a workaround by setting the model in instructions and
    relying on the global default client configured in connection.py.
    """
    # Note: We don't pass model to Agent constructor because the SDK
    # will try to parse the prefix. Instead, we rely on the global
    # default client set in connection.py which handles OpenRouter models.
    
    todo_agent = Agent(
        name="todo_agent",
        instructions=f"""You are a helpful AI task assistant using model {model}.

**CRITICAL RULES:**
1. ALWAYS use tools when user asks to create, list, update, complete, or delete tasks
2. ALWAYS use tools when user asks to create, list, delete, or assign tags
3. User ID is ALREADY provided - never ask for it
4. If a tool call fails, try once more with corrected parameters
5. After tool calls succeed, confirm the action was completed

**Available Tools:**
- create_task: Create a new task (use when user says "create a task", "add task", "make a task")
- list_tasks: List all tasks (use when user says "show tasks", "list my tasks", "what are my tasks")
- update_task: Update a task (use when user says "update task", "change task", "edit task")
- complete_task: Mark task completed (use when user says "complete task", "mark done", "finish task")
- delete_task: Delete a task (use when user says "delete task", "remove task")
- create_tag: Create a new tag (use when user says "create tag", "add tag", "make a tag")
- list_tags: List all tags (use when user says "show tags", "list my tags")
- delete_tag: Delete a tag (use when user says "delete tag", "remove tag")
- assign_tag_to_task: Assign tag to task (use when user says "assign tag", "tag this task")
- unassign_tag_from_task: Remove tag from task (use when user says "remove tag from task")

**CRITICAL - Multi-Step Operations:**
When user asks to create a task AND add/assign a tag to it:
1. First call: create_task(title="...", priority="high", due_date="...", time_str="...")
2. Second call: create_tag(name="work", color="#FF0000")
3. Third call: assign_tag_to_task(task_id="ID_FROM_STEP_1", tag_id="ID_FROM_STEP_2")

**Date/Time Handling:**
- "tomorrow" → due_date: "tomorrow"
- "afternoon" → time_str: "afternoon"
- "morning" → time_str: "morning"
- "high priority" → priority: "high"

**Response Guidelines:**
- Be concise and friendly
- After completing an action, provide a brief summary
- Never show tool call syntax in your response
- ALWAYS call tools when user asks for actions
""",
        tools=[
            create_task,
            list_tasks,
            update_task,
            complete_task,
            delete_task,
            create_tag,
            list_tags,
            delete_tag,
            assign_tag_to_task,
            unassign_tag_from_task
        ],
        model_settings=ModelSettings(temperature=0.7, max_tokens=1000)
    )

    return todo_agent


# ============ RUNNER FUNCTION ============

async def run_agent_with_user_message(
    user_message: str,
    user_id: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    model: str = None
) -> str:
    """
    Run the todo agent with a user message.

    Args:
        user_message: The user's input message
        user_id: The user's ID (injected into tools)
        conversation_history: Optional list of previous messages
        model: Optional model override

    Returns:
        Agent's response text
    """
    # Set the current user ID for tool injection
    set_current_user_id(user_id)
    
    # Debug logging
    current_uid = get_current_user_id()
    print(f"[INFO] run_agent_with_user_message: user_id='{user_id}', global_user_id='{current_uid}'")
    print(f"[INFO] Processing message: {user_message[:100]}...")

    # Use provided model or default from config
    agent_model = model if model else model_name

    # Create agent with model settings that specify the model
    agent = create_todo_agent_with_model(agent_model)

    try:
        # Build input with conversation history
        if conversation_history:
            # Create conversation items
            input_items = []
            for msg in conversation_history:
                input_items.append({"role": msg["role"], "content": msg["content"]})
            input_items.append({"role": "user", "content": user_message})

            result = await Runner.run(
                agent,
                input_items
            )
        else:
            result = await Runner.run(
                agent,
                user_message
            )

        # Get the final output
        response_text = result.final_output if result.final_output else ""

        # If no response, try to extract from tool results
        if not response_text or response_text.strip() == "":
            # Check if we have tool call results
            if hasattr(result, 'tool_calls') and result.tool_calls:
                # Look for successful tool executions
                for tool_call in result.tool_calls:
                    if hasattr(tool_call, 'output') and tool_call.output:
                        try:
                            output_data = json.loads(str(tool_call.output))
                            if output_data.get('success'):
                                response_text = output_data.get('message', 'Task completed successfully')
                                break
                        except:
                            pass
            
            # Try different attributes
            for attr in ['output', 'final_output', 'last_output', 'response']:
                if hasattr(result, attr):
                    val = getattr(result, attr)
                    if val:
                        try:
                            output_data = json.loads(str(val))
                            if output_data.get('success'):
                                response_text = output_data.get('message', 'Task completed successfully')
                                break
                        except:
                            response_text = str(val)
                            break

            # If still no response, generate a default one
            if not response_text or response_text.strip() == "":
                response_text = "I've completed your request. Please check your tasks list."

        print(f"[INFO] Agent response: {response_text[:200]}...")
        return response_text

    except Exception as e:
        print(f"Agent run error: {e}")
        import traceback
        traceback.print_exc()
        return f"I encountered an error: {str(e)}"


# ============ SYNC RUNNER (for testing) ============

def run_agent_sync(
    user_message: str,
    user_id: str,
    model: str = None
) -> str:
    """
    Run the todo agent synchronously (for testing).
    
    Args:
        user_message: The user's input message
        user_id: The user's ID
        model: Optional model override
    
    Returns:
        Agent's response text
    """
    import asyncio
    return asyncio.run(run_agent_with_user_message(user_message, user_id, model=model))


# ============ MAIN (for direct testing) ============

if __name__ == "__main__":
    print("=== Todo Agent Test ===")
    print(f"Using API Provider: {API_PROVIDER}")
    print(f"Using Model: {model_name}")
    print()
    
    # Get user ID (for testing, use a fixed UUID)
    test_user_id = "550e8400-e29b-41d4-a716-446655440000"
    set_current_user_id(test_user_id)
    
    agent = create_todo_agent()
    
    while True:
        command = input("\nEnter command (or type your natural language request): ").strip()
        
        if command.lower() in ['q', 'quit', 'exit']:
            print("Goodbye!")
            break
        
        if not command:
            continue
        
        # Run the agent with the user's input
        print("\nProcessing...")
        
        try:
            result = Runner.run_sync(
                agent,
                command
            )
            
            print(f"\n{result.final_output}")
        except Exception as e:
            print(f"\nError: {str(e)}")

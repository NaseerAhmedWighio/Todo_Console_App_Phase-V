import asyncio
import logging
import httpx
import json
import traceback
from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv
from sqlmodel import Session, select
from uuid import UUID

from ..models.conversation import Conversation
from ..models.message import Message
from ..models.user import User
from ..database.session import get_session
from .mcp_server import MCPServer

# Import OpenAI Agents SDK lazily to avoid OpenAPI schema generation issues
# The actual import happens only when needed during runtime
AGENTS_SDK_AVAILABLE = False
_run_agent_with_user_message = None
_model_name = os.getenv("CHAT_MODEL", "meta-llama/llama-3.2-3b-instruct:free")
_api_provider = "openrouter"

def _load_agents_sdk():
    """Load Agents SDK only when needed"""
    global AGENTS_SDK_AVAILABLE, _run_agent_with_user_message, _model_name, _api_provider
    try:
        from agents_sdk.todo_agent import run_agent_with_user_message, model_name, API_PROVIDER
        AGENTS_SDK_AVAILABLE = True
        _run_agent_with_user_message = run_agent_with_user_message
        _model_name = model_name
        _api_provider = API_PROVIDER
        print(f"[OK] Agents SDK enabled - Provider: {API_PROVIDER}, Model: {model_name}")
    except ImportError as e:
        AGENTS_SDK_AVAILABLE = False
        print(f"[WARN] Agents SDK not available: {e}")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class ChatService:
    """
    Enhanced Chat Service with comprehensive task management
    and simple error responses to reduce token usage
    """

    def __init__(self, mcp_server: MCPServer):
        self.mcp_server = mcp_server
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"

        # Simple error responses to reduce token billing
        self.error_responses = {
            "AUTH_REQUIRED": "Please login to use this feature.",
            "NOT_FOUND": "Item not found.",
            "INVALID_ID": "Invalid ID provided.",
            "ACCESS_DENIED": "You don't have permission to do that.",
            "CREATE_FAILED": "Failed to create. Please try again.",
            "UPDATE_FAILED": "Failed to update. Please try again.",
            "DELETE_FAILED": "Failed to delete. Please try again.",
            "LIST_FAILED": "Failed to retrieve. Please try again.",
            "SEARCH_FAILED": "Search failed. Please try again.",
            "DUPLICATE": "This already exists.",
            "ALREADY_ASSIGNED": "Already assigned.",
            "COMPLETE_FAILED": "Failed to complete task.",
            "ASSIGN_FAILED": "Failed to assign.",
            "DEFAULT": "An error occurred. Please try again."
        }

    def _get_simple_error(self, error_code: str = None) -> str:
        """Get simple error message based on error code"""
        if error_code and error_code in self.error_responses:
            return self.error_responses[error_code]
        return self.error_responses["DEFAULT"]

    async def process_message(
        self,
        user_id: str,
        user_message: str,
        conversation_id: Optional[str] = None
    ) -> str:
        """
        Process user message using AI Agent SDK with tool calling.
        """
        logger.info(f"Processing message for user {user_id}")

        try:
            # Get or create conversation
            conversation = await self._get_or_create_conversation(user_id, conversation_id)

            # Get conversation history (last 10 messages for context)
            messages = await self._get_conversation_history(conversation.id)

            # Prepare conversation history for agent
            conversation_history = []
            for msg in messages[-10:]:
                conversation_history.append({
                    "role": msg.role,
                    "content": msg.content
                })

            # Use AI Agent SDK for intelligent tool calling
            return await self._process_with_agent_sdk(
                user_id=user_id,
                user_message=user_message,
                conversation_history=conversation_history
            )

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return "I encountered an error. Please try again."

    async def _process_with_agent_sdk(
        self,
        user_id: str,
        user_message: str,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """
        Process message using AI Agent SDK with intelligent tool calling.
        This enables multi-step operations like create task + assign tag automatically.
        """
        try:
            # Load agents SDK if available
            _load_agents_sdk()

            if AGENTS_SDK_AVAILABLE and _run_agent_with_user_message:
                logger.info(f"Using Agent SDK for processing: {user_message[:50]}...")
                
                # Run agent with conversation history
                response = await _run_agent_with_user_message(
                    user_message=user_message,
                    user_id=user_id,
                    conversation_history=conversation_history
                )
                
                logger.info(f"Agent SDK response: {response[:100] if response else 'empty'}...")
                return response or "I've completed your request. Please check your tasks."
            else:
                logger.info("Agent SDK not available, falling back to direct tools")
                # Fallback to direct tool execution
                return await self._process_with_direct_tools(
                    user_id=user_id,
                    user_message=user_message,
                    conversation_history=conversation_history
                )

        except Exception as e:
            logger.error(f"Agent SDK error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Fallback to direct tools
            return await self._process_with_direct_tools(
                user_id=user_id,
                user_message=user_message,
                conversation_history=conversation_history
            )

    async def _process_with_direct_tools(
        self,
        user_id: str,
        user_message: str,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """
        Process message using DIRECT tool execution via MCP Server.
        Includes natural language parsing for dates, times, and tags.
        """
        try:
            # Get database session and create MCP server
            from app.database.session import get_session
            from app.services.mcp_server import MCPServer
            from app.services.natural_language_parser import extract_task_details
            
            session = next(get_session())
            mcp = MCPServer(session)
            
            message_lower = user_message.lower()
            
            # Parse user intent and call tools directly
            if 'create' in message_lower and 'task' in message_lower:
                # Extract all task details using NLP
                details = extract_task_details(user_message)
                
                # Debug logging
                logger.info(f"Extracted task details: title={details['title']}, due_date={details['due_date']}, time_str={details['time_str']}, tag={details['tag_name']}")

                # Call create_task tool from MCP server
                # Pass both due_date (ISO string) and time_str for proper parsing
                result = mcp.create_task_tool(
                    title=details['title'],
                    description=details['description'],
                    priority=details['priority'],
                    due_date=details['due_date'] if details['due_date'] else None,
                    time_str=details['time_str'] if details['time_str'] else None,
                    user_id=user_id
                )

                if not result.get('success'):
                    return f"Failed to create task: {result.get('message')}"

                # Only commit if successful
                session.commit()

                task_id = result['data']['id']
                response = f"[OK] Task '{details['title']}' created successfully with {details['priority']} priority"

                # Add date/time info
                if details['due_date']:
                    response += f" for {details['due_date']}"
                if details['time_str']:
                    response += f" at {details['time_str']}"

                # Handle tag if specified - TAG IS MANDATORY WHEN MENTIONED
                if details['tag_name']:
                    logger.info(f"Creating/finding tag: {details['tag_name']}")

                    # Create tag if it doesn't exist
                    tag_result = mcp.create_tag_tool(
                        name=details['tag_name'],
                        color=details['tag_color'],
                        user_id=user_id
                    )

                    if tag_result.get('success') or 'already exists' in tag_result.get('message', '').lower():
                        # Get tag ID (either from creation or existing)
                        tag_id = None
                        if tag_result.get('success'):
                            tag_id = tag_result['data']['id']
                            logger.info(f"Tag created with ID: {tag_id}")
                        else:
                            # Tag already exists, get it from list
                            tags_result = mcp.list_tags_tool(user_id=user_id)
                            for tag in tags_result.get('data', []):
                                if tag['name'].lower() == details['tag_name'].lower():
                                    tag_id = tag['id']
                                    logger.info(f"Found existing tag with ID: {tag_id}")
                                    break

                        if tag_id:
                            # Assign tag to task - THIS IS MANDATORY
                            assign_result = mcp.assign_tag_to_task_tool(
                                task_id=task_id,
                                tag_id=tag_id,
                                user_id=user_id
                            )

                            if assign_result.get('success'):
                                response += f" and tagged as '{details['tag_name']}'"
                            elif 'already assigned' in assign_result.get('message', '').lower():
                                response += f" with tag '{details['tag_name']}' (already assigned)"
                            else:
                                logger.error(f"Failed to assign tag: {assign_result}")
                                response += " [Tag creation OK, assignment failed]"
                        else:
                            logger.error(f"Could not find tag ID for: {details['tag_name']}")
                    else:
                        logger.error(f"Failed to create tag: {tag_result}")
                
                response += "."
                return response
            
            elif 'list' in message_lower and ('task' in message_lower or 'tasks' in message_lower):
                # Check if filtering by tag
                if 'tag' in message_lower or 'tagged' in message_lower:
                    # Get tag name
                    tag_name = None
                    for word in message_lower.split():
                        if word not in ['tag', 'tagged', 'with', 'by']:
                            tag_name = word.title()
                            break
                    
                    if tag_name:
                        # Get tags to find ID
                        tags_result = mcp.list_tags_tool(user_id=user_id)
                        tag_id = None
                        for tag in tags_result.get('data', []):
                            if tag['name'].lower() == tag_name.lower():
                                tag_id = tag['id']
                                break
                        
                        if tag_id:
                            result = mcp.list_tasks_tool(user_id=user_id, tag_id=tag_id)
                        else:
                            return f"Tag '{tag_name}' not found."
                    else:
                        result = mcp.list_tasks_tool(user_id=user_id)
                else:
                    # Check for priority filter
                    priority = None
                    if 'high' in message_lower:
                        priority = 'high'
                    elif 'urgent' in message_lower:
                        priority = 'urgent'
                    elif 'low' in message_lower:
                        priority = 'low'
                    elif 'medium' in message_lower:
                        priority = 'medium'
                    
                    # Check for status filter
                    status = 'all'
                    if 'completed' in message_lower or 'done' in message_lower:
                        status = 'completed'
                    elif 'pending' in message_lower or 'incomplete' in message_lower:
                        status = 'pending'
                    
                    result = mcp.list_tasks_tool(user_id=user_id, priority=priority, status=status)
                
                if result.get('success'):
                    tasks = result.get('data', [])
                    if tasks:
                        task_list = "\n".join([
                            f"  - {t['title']} ({t['priority']}) - Due: {t.get('due_date', 'None')}" + 
                            (f" - Tags: {', '.join([tag['name'] for tag in t.get('tags', [])])}" if t.get('tags') else "")
                            for t in tasks
                        ])
                        return f"Found {len(tasks)} tasks:\n{task_list}"
                    else:
                        return "You have no tasks."
                else:
                    return f"Failed to list tasks: {result.get('message')}"
            
            elif ('complete' in message_lower or ('mark' in message_lower and 'done' in message_lower) or ('mark' in message_lower and 'completed' in message_lower)):
                # Extract task title or ID from message
                task_identifier = self._extract_task_identifier(user_message, user_id, mcp)
                if task_identifier:
                    result = mcp.complete_task_tool(task_id=task_identifier, user_id=user_id)
                    if result.get('success'):
                        return f"[OK] Task '{result['data'].get('title', 'task')}' marked as completed."
                    else:
                        return f"Failed to complete task: {result.get('message')}"
                else:
                    return "I couldn't find the task. Please provide the task title or ID."

            elif 'delete' in message_lower and 'task' in message_lower:
                # Extract task title or ID from message
                task_identifier = self._extract_task_identifier(user_message, user_id, mcp)
                if task_identifier:
                    result = mcp.delete_task_tool(task_id=task_identifier, user_id=user_id)
                    if result.get('success'):
                        return f"[OK] Task '{result['data'].get('title', 'task')}' deleted successfully."
                    else:
                        return f"Failed to delete task: {result.get('message')}"
                else:
                    return "I couldn't find the task. Please provide the task title or ID."

            elif 'update' in message_lower and 'task' in message_lower:
                return "To update a task, please specify what to change (title, description, priority, etc.)."
            
            elif 'tag' in message_lower:
                if 'create' in message_lower:
                    # Extract tag name using multiple patterns
                    tag_name = None
                    tag_color = "#3B82F6"  # Default blue

                    # Pattern 1: "create a tag of [name]"
                    if 'tag of ' in message_lower:
                        tag_name = message_lower.split('tag of ', 1)[1].split(' with ')[0].split(' for ')[0].strip().title()
                    # Pattern 2: "create a tag called/named [name]"
                    elif 'called ' in message_lower or 'named ' in message_lower:
                        keyword = 'called ' if 'called ' in message_lower else 'named '
                        tag_name = message_lower.split(keyword, 1)[1].split(' with ')[0].split(' for ')[0].strip().title()
                    # Pattern 3: "create [name] tag"
                    elif 'create ' in message_lower and ' tag' in message_lower:
                        parts = message_lower.split('create ', 1)
                        if len(parts) > 1:
                            rest = parts[1].split(' tag')[0].strip()
                            # Remove articles
                            rest = rest.replace('a ', '').replace('an ', '').strip()
                            tag_name = rest.title()

                    # If still no tag name, try to extract word after "tag"
                    if not tag_name:
                        words = message_lower.split()
                        for i, word in enumerate(words):
                            if word == 'tag' and i + 1 < len(words):
                                next_word = words[i + 1]
                                if next_word not in ['of', 'called', 'named', 'with', 'for', 'a', 'an', 'the']:
                                    tag_name = next_word.title()
                                    break

                    # If still nothing, use default
                    if not tag_name:
                        tag_name = "Tag"

                    # Extract color
                    color_map = {
                        'red': '#FF0000', 'blue': '#3B82F6', 'green': '#10B981',
                        'yellow': '#F59E0B', 'purple': '#8B5CF6', 'orange': '#F97316',
                        'pink': '#EC4899'
                    }
                    for color_name, color_code in color_map.items():
                        if color_name in message_lower:
                            tag_color = color_code
                            break

                    result = mcp.create_tag_tool(name=tag_name, color=tag_color, user_id=user_id)

                    if result.get('success'):
                        return f"[OK] Tag '{tag_name}' created successfully with color {tag_color}."
                    elif 'already exists' in result.get('message', '').lower():
                        return f"Tag '{tag_name}' already exists."
                    else:
                        return f"Failed to create tag: {result.get('message')}"
                
                elif 'list' in message_lower or 'show' in message_lower:
                    result = mcp.list_tags_tool(user_id=user_id)
                    if result.get('success'):
                        tags = result.get('data', [])
                        if tags:
                            tag_list = "\n".join([f"  - {t['name']} ({t['color']})" for t in tags])
                            return f"Found {len(tags)} tags:\n{tag_list}"
                        else:
                            return "You have no tags."
                    else:
                        return f"Failed to list tags: {result.get('message')}"
                
                elif 'assign' in message_lower or 'add' in message_lower:
                    return "To assign a tag, please specify the task and tag name."
                
                elif 'delete' in message_lower or 'remove' in message_lower:
                    return "To delete a tag, please specify the tag name."
            
            # Default response for unrecognized commands
            return "I can help you with: create tasks (with dates/times/tags), list tasks, complete tasks, delete tasks, and manage tags. What would you like to do?"
            
        except Exception as e:
            logger.error(f"Direct tool execution error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Fallback to legacy API
            return await self._process_with_legacy_api(user_id, user_message, conversation_history)

    async def _process_with_legacy_api(
        self,
        user_id: str,
        user_message: str,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Legacy processing using direct OpenRouter API calls (fallback)"""
        try:
            # Prepare system prompt
            system_prompt = f"""You are a helpful AI task assistant. You can create tasks, list them, update them, complete them, and delete them.
You can also create tags and assign them to tasks.

Current user ID: {user_id}"""

            # Prepare messages for AI
            ai_messages = [
                {"role": "system", "content": system_prompt},
                *conversation_history,
                {"role": "user", "content": user_message}
            ]

            # Get model from environment (same as agent SDK)
            model = os.getenv("CHAT_MODEL", _model_name)

            # Prepare request payload
            payload = {
                "model": model,
                "messages": ai_messages,
                "max_tokens": 500,
                "temperature": 0.7
            }

            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "Todo App Chat"
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.openrouter_url,
                    headers=headers,
                    json=payload
                )

                if response.status_code != 200:
                    logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                    return "I'm having trouble connecting right now. Please try again."

                response_data = response.json()
                choices = response_data.get('choices', [])

                if not choices:
                    return "I received an unexpected response. Please try again."

                return choices[0].get('message', {}).get('content', 'How can I help you?')

        except Exception as e:
            logger.error(f"Legacy API error: {str(e)}")
            return "I encountered an error. Please try again."

    async def _execute_tool(self, function_name: str, function_args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return result"""
        try:
            logger.info(f"Tool execution started: {function_name}")
            logger.info(f"Tool arguments: {function_args}")
            
            if function_name == "create_task":
                return self.mcp_server.create_task_tool(**function_args)
            elif function_name == "list_tasks":
                return self.mcp_server.list_tasks_tool(**function_args)
            elif function_name == "update_task":
                return self.mcp_server.update_task_tool(**function_args)
            elif function_name == "complete_task":
                return self.mcp_server.complete_task_tool(**function_args)
            elif function_name == "delete_task":
                return self.mcp_server.delete_task_tool(**function_args)
            elif function_name == "create_tag":
                return self.mcp_server.create_tag_tool(**function_args)
            elif function_name == "list_tags":
                return self.mcp_server.list_tags_tool(**function_args)
            elif function_name == "assign_tag_to_task":
                return self.mcp_server.assign_tag_to_task_tool(**function_args)
            elif function_name == "delete_tag":
                return self.mcp_server.delete_tag_tool(**function_args)
            elif function_name == "unassign_tag_from_task":
                return self.mcp_server.unassign_tag_from_task_tool(**function_args)
            elif function_name == "search_tasks":
                return self.mcp_server.search_tasks_tool(**function_args)
            elif function_name == "filter_tasks":
                return self.mcp_server.filter_tasks_tool(**function_args)
            elif function_name == "create_reminder":
                return self.mcp_server.create_reminder_tool(**function_args)
            elif function_name == "list_reminders":
                return self.mcp_server.list_reminders_tool(**function_args)
            elif function_name == "delete_reminder":
                return self.mcp_server.delete_reminder_tool(**function_args)
            else:
                return {
                    "success": False,
                    "message": f"Unknown function: {function_name}",
                    "error_code": "UNKNOWN_FUNCTION"
                }
        except Exception as e:
            logger.error(f"Tool execution error: {str(e)}")
            logger.error(f"Tool traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "message": f"Tool execution failed: {str(e)}",
                "error_code": "EXECUTION_FAILED"
            }

    def _extract_params_from_message(self, user_message: str, function_name: str) -> Dict[str, Any]:
        """
        Extract parameters from user message when model fails to provide complete arguments.
        This is a fallback for when the model truncates tool call arguments.
        """
        import re

        params = {}
        message_lower = user_message.lower()

        if function_name == "create_task":
            # Extract title - look for text after "create a task to" or similar
            title_patterns = [
                r"create a task to (.+?)(?: with| at| for|$)",
                r"create task to (.+?)(?: with| at| for|$)",
                r"add task to (.+?)(?: with| at| for|$)",
            ]
            for pattern in title_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    params["title"] = match.group(1).strip().title()
                    break

            # If no title found, use a default
            if "title" not in params:
                params["title"] = "Untitled Task"

            # Extract priority
            if "high priority" in message_lower or "high prioraty" in message_lower:
                params["priority"] = "high"
            elif "urgent priority" in message_lower:
                params["priority"] = "urgent"
            elif "low priority" in message_lower:
                params["priority"] = "low"
            else:
                params["priority"] = "medium"

            # Extract time
            if "afternoon" in message_lower:
                params["time_str"] = "afternoon"
            elif "morning" in message_lower:
                params["time_str"] = "morning"
            elif "evening" in message_lower:
                params["time_str"] = "evening"
            elif "night" in message_lower:
                params["time_str"] = "night"

            # Extract date
            if "tomorrow" in message_lower:
                params["due_date"] = "tomorrow"
            elif "today" in message_lower:
                params["due_date"] = "today"
            elif "next week" in message_lower:
                params["due_date"] = "next week"

        elif function_name == "create_tag":
            # Extract tag name - look for "tag of X" or "tag X"
            tag_match = re.search(r"tag of (\w+)", message_lower)
            if tag_match:
                params["name"] = tag_match.group(1).strip().title()
            else:
                tag_match = re.search(r"add tag (\w+)", message_lower)
                if tag_match:
                    params["name"] = tag_match.group(1).strip().title()

            if "name" not in params:
                params["name"] = "General"

            params["color"] = "#FF0000"  # Default red for work tags

        return params

    def _extract_task_identifier(self, user_message: str, user_id: str, mcp) -> Optional[str]:
        """
        Extract task identifier (ID or title) from user message.
        First tries to find a UUID, then searches by title.

        Args:
            user_message: User's input message
            user_id: User ID for ownership verification
            mcp: MCP server instance to query tasks

        Returns:
            Task ID if found, None otherwise
        """
        import re

        message_lower = user_message.lower()

        # Pattern 1: Try to find UUID in message
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        uuid_match = re.search(uuid_pattern, user_message, re.IGNORECASE)
        if uuid_match:
            return uuid_match.group(0)

        # Pattern 2: Look for task title in quotes
        quoted_pattern = r'["\']([^"\']+)["\']'
        quoted_match = re.search(quoted_pattern, user_message)
        if quoted_match:
            task_title = quoted_match.group(1)
            # Search for task by title
            return self._find_task_by_title(task_title, user_id, mcp)

        # Pattern 3: Look for task title after keywords
        # "mark my task X", "complete task X", "delete task X", "update task X"
        title_keywords = [
            r'(?:mark|complete|delete|update)\s+(?:my\s+)?(?:task\s+)?["\']?([^"\']+?)["\']?\s+(?:as|for|with|to|at|in|on|$)',
            r'(?:mark|complete|delete|update)\s+(?:my\s+)?task\s+([^\s]+(?:\s+[^\s]+)?)',
        ]

        for pattern in title_keywords:
            match = re.search(pattern, message_lower)
            if match:
                task_title = match.group(1).strip().title()
                # Clean up common endings
                for ending in [' as completed', ' as complete', ' as done', ' from list', ' permanently']:
                    task_title = task_title.replace(ending.title(), '').strip()
                    task_title = task_title.replace(ending.lower(), '').strip()
                if task_title:
                    return self._find_task_by_title(task_title, user_id, mcp)

        # Pattern 4: Extract words that look like a task title
        # Look for content between common verbs and prepositions
        if 'task' in message_lower:
            parts = message_lower.split('task', 1)
            if len(parts) > 1:
                rest = parts[1].strip()
                # Remove common prepositions at the start
                for prep in ['to', 'of', 'for', 'with', 'from', 'in', 'on', 'at']:
                    if rest.startswith(prep + ' '):
                        rest = rest[len(prep) + 1:].strip()
                        break
                # Extract until a preposition or end
                title_words = []
                for word in rest.split():
                    if word in ['as', 'to', 'for', 'with', 'from', 'in', 'on', 'at', 'by']:
                        break
                    title_words.append(word)
                if title_words:
                    task_title = ' '.join(title_words).strip().title()
                    # Clean up
                    if task_title.endswith('As Completed'):
                        task_title = task_title[:-14]
                    if task_title.endswith('As Complete'):
                        task_title = task_title[:-13]
                    if task_title.endswith('As Done'):
                        task_title = task_title[:-9]
                    if task_title:
                        return self._find_task_by_title(task_title, user_id, mcp)

        return None

    def _find_task_by_title(self, task_title: str, user_id: str, mcp) -> Optional[str]:
        """
        Find a task by its title for a specific user.

        Args:
            task_title: Title to search for
            user_id: User ID for ownership verification
            mcp: MCP server instance

        Returns:
            Task ID if found, None otherwise
        """
        # Get all tasks for user
        tasks_result = mcp.list_tasks_tool(user_id=user_id, limit=100)
        if tasks_result.get('success'):
            tasks = tasks_result.get('data', [])
            # Try exact match first (case-insensitive)
            for task in tasks:
                if task['title'].lower() == task_title.lower():
                    return task['id']
            # Try partial match
            for task in tasks:
                if task_title.lower() in task['title'].lower() or task['title'].lower() in task_title.lower():
                    return task['id']
        return None

    async def _get_or_create_conversation(
        self,
        user_id: str,
        conversation_id: Optional[str]
    ) -> Conversation:
        """Get or create conversation"""
        with next(get_session()) as session:
            if conversation_id:
                try:
                    conv_uuid = UUID(conversation_id)
                    conversation = session.get(Conversation, conv_uuid)
                    if conversation and str(conversation.user_id) == user_id:
                        return conversation
                except:
                    pass

            # Create new conversation
            conversation = Conversation(user_id=UUID(user_id))
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            return conversation

    async def _get_conversation_history(
        self,
        conversation_id: UUID
    ) -> list:
        """Get conversation history"""
        with next(get_session()) as session:
            messages = session.exec(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.timestamp.asc())
            ).all()
            return messages

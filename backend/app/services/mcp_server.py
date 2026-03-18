import json
import re
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from ..models.todo import Todo
from ..models.tag import Tag
from ..models.task_tag import TaskTag
from ..models.reminder import Reminder
from ..database.session import Session
from sqlmodel import select, col
import uuid
import asyncio

# Import WebSocket manager for live updates
try:
    from ..api.websocket_manager import manager as websocket_manager
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    websocket_manager = None


class ToolResult(BaseModel):
    """Standardized result for all tool operations"""
    success: bool
    message: str
    data: Any = None
    error_code: str = None

    def dict(self):
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "error_code": self.error_code
        }


class MCPServer:
    """
    Enhanced MCP server with comprehensive task management tools
    including reminders, priorities, tags, and advanced search
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def _broadcast_websocket(self, update_type: str, event_type: str, data: dict, user_id: str):
        """Helper to broadcast WebSocket updates without blocking"""
        if not WEBSOCKET_AVAILABLE or not websocket_manager:
            return
        
        try:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(
                        websocket_manager.broadcast_task_update(event_type, data, user_id) if update_type == "task" else
                        websocket_manager.broadcast_tag_update(event_type, data, user_id) if update_type == "tag" else
                        websocket_manager.broadcast_reminder_update(event_type, data, user_id)
                    )
                else:
                    if update_type == "task":
                        loop.run_until_complete(websocket_manager.broadcast_task_update(event_type, data, user_id))
                    elif update_type == "tag":
                        loop.run_until_complete(websocket_manager.broadcast_tag_update(event_type, data, user_id))
                    else:
                        loop.run_until_complete(websocket_manager.broadcast_reminder_update(event_type, data, user_id))
            except RuntimeError:
                asyncio.run(
                    websocket_manager.broadcast_task_update(event_type, data, user_id) if update_type == "task" else
                    websocket_manager.broadcast_tag_update(event_type, data, user_id) if update_type == "tag" else
                    websocket_manager.broadcast_reminder_update(event_type, data, user_id)
                )
        except Exception as notify_error:
            print(f"WebSocket notification error: {notify_error}")

    def parse_natural_language_datetime(
        self,
        date_str: str,
        time_str: Optional[str] = None
    ) -> Optional[datetime]:
        """
        Parse natural language date and time into datetime object.

        Handles:
        - Relative dates: tomorrow, next week, in 2 days
        - Time periods: morning (9AM), afternoon (2PM), evening (6PM), night (9PM)
        - Specific times: 9pm, 14:00, 2:30 PM
        - Combined: tomorrow 9pm, next Monday morning

        Args:
            date_str: Natural language date (e.g., "tomorrow", "next Monday", "2024-01-20")
            time_str: Optional time specification (e.g., "9pm", "morning", "14:00")

        Returns:
            datetime object or None if parsing fails
        """
        if not date_str:
            return None

        now = datetime.now()
        result_date = now

        date_str_lower = date_str.lower().strip()

        # Handle relative dates
        if date_str_lower in ['tomorrow', 'tmr', 'tmrw']:
            result_date = now + timedelta(days=1)
        elif date_str_lower in ['today']:
            result_date = now
        elif date_str_lower in ['yesterday']:
            result_date = now - timedelta(days=1)
        elif date_str_lower.startswith('in '):
            # "in 2 days", "in 3 weeks"
            match = re.match(r'in\s+(\d+)\s*(day|days|week|weeks|month|months)', date_str_lower)
            if match:
                value = int(match.group(1))
                unit = match.group(2)
                if 'week' in unit:
                    result_date = now + timedelta(weeks=value)
                elif 'month' in unit:
                    result_date = now + timedelta(days=value * 30)
                else:
                    result_date = now + timedelta(days=value)
        elif date_str_lower.startswith('next '):
            # "next Monday", "next week"
            day_match = re.match(r'next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', date_str_lower)
            if day_match:
                day_name = day_match.group(1)
                days_ahead = self._get_days_until_day(day_name)
                if days_ahead == 0:  # If today, move to next week
                    days_ahead = 7
                result_date = now + timedelta(days=days_ahead)
            elif 'week' in date_str_lower:
                result_date = now + timedelta(weeks=1)
        else:
            # Try to parse as ISO format or standard date
            try:
                # If it's already an ISO date (YYYY-MM-DD), parse it directly
                parsed = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                result_date = parsed
            except:
                # Try common date formats
                for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%B %d, %Y', '%b %d, %Y']:
                    try:
                        result_date = datetime.strptime(date_str, fmt)
                        break
                    except:
                        continue

        # Handle time specification
        if time_str:
            result_date = self._parse_time_and_apply(result_date, time_str)

        return result_date

    def _get_days_until_day(self, day_name: str) -> int:
        """Get number of days until a specific day of the week"""
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        try:
            target_day = days.index(day_name.lower())
            current_day = datetime.now().weekday()
            days_ahead = target_day - current_day
            if days_ahead < 0:
                days_ahead += 7
            return days_ahead
        except:
            return 0

    def _parse_time_and_apply(self, base_date: datetime, time_str: str) -> datetime:
        """
        Parse time string and apply to base date.
        
        Handles:
        - Time periods: morning, afternoon, evening, night
        - Specific times: 9pm, 14:00, 2:30 PM, 9:00 am
        """
        time_str_lower = time_str.lower().strip()
        
        # Default times for time periods
        time_period_hours = {
            'morning': (9, 0),      # 9:00 AM
            'afternoon': (14, 0),   # 2:00 PM
            'evening': (18, 0),     # 6:00 PM
            'night': (21, 0),       # 9:00 PM
            'midnight': (0, 0),     # 12:00 AM
            'noon': (12, 0),        # 12:00 PM
        }
        
        # Check for time period keywords
        for period, (hour, minute) in time_period_hours.items():
            if period in time_str_lower:
                return base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Try to parse specific time
        time_patterns = [
            (r'(\d{1,2}):(\d{2})\s*(am|pm)?', self._parse_time_hh_mm),
            (r'(\d{1,2})\s*(am|pm)', self._parse_time_h),
            (r'(\d{4})', self._parse_time_military),
        ]
        
        for pattern, parser in time_patterns:
            match = re.search(pattern, time_str_lower)
            if match:
                hour, minute = parser(match)
                if hour is not None and 0 <= hour <= 23 and 0 <= minute <= 59:
                    return base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        return base_date

    def _parse_time_hh_mm(self, match) -> Tuple[Optional[int], Optional[int]]:
        """Parse HH:MM AM/PM format"""
        try:
            hour = int(match.group(1))
            minute = int(match.group(2))
            am_pm = match.group(3)
            
            if am_pm:
                if am_pm.lower() == 'pm' and hour != 12:
                    hour += 12
                elif am_pm.lower() == 'am' and hour == 12:
                    hour = 0
            
            return (hour, minute)
        except:
            return (None, None)

    def _parse_time_h(self, match) -> Tuple[Optional[int], Optional[int]]:
        """Parse H AM/PM format"""
        try:
            hour = int(match.group(1))
            am_pm = match.group(2)
            
            if am_pm:
                if am_pm.lower() == 'pm' and hour != 12:
                    hour += 12
                elif am_pm.lower() == 'am' and hour == 12:
                    hour = 0
            
            return (hour, 0)
        except:
            return (None, None)

    def _parse_time_military(self, match) -> Tuple[Optional[int], Optional[int]]:
        """Parse military time HHMM format"""
        try:
            time_str = match.group(1)
            hour = int(time_str[:2])
            minute = int(time_str[2:])
            return (hour, minute)
        except:
            return (None, None)

    def _get_user_id(self, provided_user_id: Optional[str] = None) -> Optional[uuid.UUID]:
        """Get user ID from parameter or session"""
        effective_user_id = provided_user_id or getattr(self, '_current_user_id', None)
        if effective_user_id:
            try:
                return uuid.UUID(effective_user_id)
            except:
                return None
        return None

    def _safe_uuid(self, uuid_str: str) -> Optional[uuid.UUID]:
        """Safely convert string to UUID"""
        try:
            return uuid.UUID(uuid_str)
        except:
            return None

    def _calculate_reminder_time(
        self,
        due_date: datetime,
        timing_minutes: int = 0,
        timing_days: Optional[int] = None
    ) -> datetime:
        """Calculate when reminder should be sent"""
        if due_date.tzinfo is None:
            due_date = due_date.replace(tzinfo=timezone.utc)
        
        if timing_days is not None and timing_days > 0:
            return due_date - timedelta(days=timing_days)
        else:
            return due_date - timedelta(minutes=timing_minutes)

    # ========== TASK TOOLS ==========

    def create_task_tool(
        self,
        title: str,
        user_id: str = None,
        description: str = "",
        priority: str = "medium",
        due_date: str = None,
        time_str: str = None
    ) -> Dict[str, Any]:
        """Create a new task with full details"""
        try:
            user_uuid = self._get_user_id(user_id)
            if not user_uuid:
                return ToolResult(
                    success=False,
                    message="User not authenticated. Please login first.",
                    error_code="AUTH_REQUIRED"
                ).dict()

            # Parse due_date using natural language parser
            due_date_dt = None
            if due_date:
                # Check if it's already an ISO date string (YYYY-MM-DD)
                import re
                if re.match(r'^\d{4}-\d{2}-\d{2}$', due_date):
                    # It's already a parsed date from NLP parser, use it directly
                    try:
                        # Parse the date and set time to noon to avoid timezone issues
                        due_date_dt = datetime.strptime(due_date, '%Y-%m-%d')
                        due_date_dt = due_date_dt.replace(hour=12, minute=0, second=0)
                        print(f"[DEBUG] MCP create_task: ISO date detected: {due_date}, parsed to: {due_date_dt}")
                        # If time_str is provided, apply it
                        if time_str:
                            due_date_dt = self._parse_time_and_apply(due_date_dt, time_str)
                            print(f"[DEBUG] MCP create_task: Time applied: {time_str}, result: {due_date_dt}")
                    except Exception as e:
                        print(f"[DEBUG] MCP create_task: Failed to parse ISO date {due_date}: {e}")
                else:
                    print(f"[DEBUG] MCP create_task: Using natural language parser for: {due_date}")
                    # Use natural language parser for relative dates
                    due_date_dt = self.parse_natural_language_datetime(due_date, time_str)
                    if not due_date_dt:
                        # Fallback to ISO format parsing
                        try:
                            due_date_dt = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                        except:
                            pass
                    print(f"[DEBUG] MCP create_task: Parsed result: {due_date_dt}")

            new_task = Todo(
                title=title,
                description=description or "",
                is_completed=False,
                priority=priority or "medium",
                due_date=due_date_dt,
                user_id=user_uuid
            )

            self.db_session.add(new_task)
            self.db_session.commit()
            self.db_session.refresh(new_task)

            # Broadcast live update via WebSocket
            if WEBSOCKET_AVAILABLE and websocket_manager:
                task_data = {
                    "id": str(new_task.id),
                    "title": new_task.title,
                    "description": new_task.description,
                    "priority": new_task.priority,
                    "is_completed": new_task.is_completed,
                    "due_date": new_task.due_date.isoformat() if new_task.due_date else None,
                    "created_at": new_task.created_at.isoformat() if new_task.created_at else None,
                    "updated_at": new_task.updated_at.isoformat() if new_task.updated_at else None
                }
                self._broadcast_websocket("task", "created", task_data, str(user_uuid))

            return ToolResult(
                success=True,
                message=f"Task '{title}' created successfully",
                data={
                    "id": str(new_task.id),
                    "title": new_task.title,
                    "priority": new_task.priority,
                    "due_date": new_task.due_date.isoformat() if new_task.due_date else None
                }
            ).dict()

        except Exception as e:
            self.db_session.rollback()
            return ToolResult(
                success=False,
                message=f"Failed to create task: {str(e)}",
                error_code="CREATE_FAILED"
            ).dict()

    def list_tasks_tool(
        self,
        user_id: str,
        status: str = None,
        priority: str = None,
        tag_id: str = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """List tasks with filters"""
        try:
            user_uuid = self._get_user_id(user_id)
            if not user_uuid:
                return ToolResult(
                    success=False,
                    message="User not authenticated",
                    error_code="AUTH_REQUIRED"
                ).dict()

            # Build query
            statement = select(Todo).where(Todo.user_id == user_uuid)

            # Apply filters
            if status == "completed":
                statement = statement.where(Todo.is_completed == True)
            elif status == "pending":
                statement = statement.where(Todo.is_completed == False)

            if priority:
                statement = statement.where(Todo.priority == priority)

            if tag_id:
                tag_uuid = self._safe_uuid(tag_id)
                if tag_uuid:
                    tag_subquery = select(TaskTag.task_id).where(TaskTag.tag_id == tag_uuid)
                    statement = statement.where(Todo.id.in_(tag_subquery))

            # Apply limit
            statement = statement.limit(limit)

            tasks = self.db_session.exec(statement).all()

            task_list = []
            for task in tasks:
                # Get tags for this task
                task_tags = self.db_session.exec(
                    select(TaskTag).where(TaskTag.task_id == task.id)
                ).all()

                task_list.append({
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "completed": task.is_completed,
                    "priority": task.priority,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "tags": [
                        {"id": str(tt.tag.id), "name": tt.tag.name, "color": tt.tag.color}
                        for tt in task_tags
                    ],
                    "created_at": task.created_at.isoformat()
                })

            return ToolResult(
                success=True,
                message=f"Found {len(task_list)} tasks",
                data=task_list
            ).dict()

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"Failed to list tasks: {str(e)}",
                error_code="LIST_FAILED"
            ).dict()

    def update_task_tool(
        self,
        task_id: str,
        user_id: str = None,
        title: str = None,
        description: str = None,
        priority: str = None,
        due_date: str = None,
        completed: bool = None
    ) -> Dict[str, Any]:
        """Update task with full details"""
        try:
            task_uuid = self._safe_uuid(task_id)
            if not task_uuid:
                return ToolResult(
                    success=False,
                    message="Invalid task ID",
                    error_code="INVALID_ID"
                ).dict()

            task = self.db_session.get(Todo, task_uuid)
            if not task:
                return ToolResult(
                    success=False,
                    message="Task not found",
                    error_code="NOT_FOUND"
                ).dict()

            # Verify ownership
            user_uuid = self._get_user_id(user_id)
            if user_uuid and task.user_id != user_uuid:
                return ToolResult(
                    success=False,
                    message="Access denied: You can only update your own tasks",
                    error_code="ACCESS_DENIED"
                ).dict()

            # Update fields
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if priority is not None:
                task.priority = priority
            if due_date is not None:
                # Use natural language parser for due_date
                parsed_date = self.parse_natural_language_datetime(due_date)
                if parsed_date:
                    task.due_date = parsed_date
                else:
                    try:
                        task.due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    except:
                        pass
            if completed is not None:
                task.is_completed = completed

            self.db_session.add(task)
            self.db_session.commit()
            self.db_session.refresh(task)

            # Broadcast live update via WebSocket
            if WEBSOCKET_AVAILABLE and websocket_manager:
                try:
                    task_data = {
                        "id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "priority": task.priority,
                        "is_completed": task.is_completed,
                        "due_date": task.due_date.isoformat() if task.due_date else None,
                        "created_at": task.created_at.isoformat() if task.created_at else None,
                        "updated_at": task.updated_at.isoformat() if task.updated_at else None
                    }
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(
                            websocket_manager.broadcast_task_update("updated", task_data, str(user_uuid))
                        )
                    finally:
                        loop.close()
                except Exception as notify_error:
                    print(f"WebSocket notification error: {notify_error}")

            return ToolResult(
                success=True,
                message=f"Task '{task.title}' updated successfully",
                data={
                    "id": str(task.id),
                    "title": task.title,
                    "priority": task.priority,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "completed": task.is_completed
                }
            ).dict()

        except Exception as e:
            self.db_session.rollback()
            return ToolResult(
                success=False,
                message=f"Failed to update task: {str(e)}",
                error_code="UPDATE_FAILED"
            ).dict()

    def complete_task_tool(self, task_id: str, user_id: str = None) -> Dict[str, Any]:
        """Mark task as completed"""
        try:
            task_uuid = self._safe_uuid(task_id)
            if not task_uuid:
                return ToolResult(
                    success=False,
                    message="Invalid task ID",
                    error_code="INVALID_ID"
                ).dict()

            task = self.db_session.get(Todo, task_uuid)
            if not task:
                return ToolResult(
                    success=False,
                    message="Task not found",
                    error_code="NOT_FOUND"
                ).dict()

            user_uuid = self._get_user_id(user_id)
            if user_uuid and task.user_id != user_uuid:
                return ToolResult(
                    success=False,
                    message="Access denied",
                    error_code="ACCESS_DENIED"
                ).dict()

            task.is_completed = True
            self.db_session.add(task)
            self.db_session.commit()
            self.db_session.refresh(task)

            # Broadcast live update via WebSocket
            if WEBSOCKET_AVAILABLE and websocket_manager:
                try:
                    task_data = {
                        "id": str(task.id),
                        "title": task.title,
                        "is_completed": True,
                        "due_date": task.due_date.isoformat() if task.due_date else None
                    }
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(
                            websocket_manager.broadcast_task_update("completed", task_data, str(user_uuid))
                        )
                    finally:
                        loop.close()
                except Exception as notify_error:
                    print(f"WebSocket notification error: {notify_error}")

            return ToolResult(
                success=True,
                message=f"Task '{task.title}' marked as completed",
                data={"id": str(task.id), "title": task.title}
            ).dict()

        except Exception as e:
            self.db_session.rollback()
            return ToolResult(
                success=False,
                message=f"Failed to complete task: {str(e)}",
                error_code="COMPLETE_FAILED"
            ).dict()

    def delete_task_tool(self, task_id: str, user_id: str = None) -> Dict[str, Any]:
        """Delete a task"""
        try:
            task_uuid = self._safe_uuid(task_id)
            if not task_uuid:
                return ToolResult(
                    success=False,
                    message="Invalid task ID",
                    error_code="INVALID_ID"
                ).dict()

            task = self.db_session.get(Todo, task_uuid)
            if not task:
                return ToolResult(
                    success=False,
                    message="Task not found",
                    error_code="NOT_FOUND"
                ).dict()

            user_uuid = self._get_user_id(user_id)
            if user_uuid and task.user_id != user_uuid:
                return ToolResult(
                    success=False,
                    message="Access denied",
                    error_code="ACCESS_DENIED"
                ).dict()

            task_title = task.title
            task_data = {
                "id": str(task.id),
                "title": task.title
            }
            self.db_session.delete(task)
            self.db_session.commit()

            # Broadcast live update via WebSocket
            if WEBSOCKET_AVAILABLE and websocket_manager:
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(
                            websocket_manager.broadcast_task_update("deleted", task_data, str(user_uuid))
                        )
                    finally:
                        loop.close()
                except Exception as notify_error:
                    print(f"WebSocket notification error: {notify_error}")

            return ToolResult(
                success=True,
                message=f"Task '{task_title}' deleted successfully",
                data={"id": str(task_id)}
            ).dict()

        except Exception as e:
            self.db_session.rollback()
            return ToolResult(
                success=False,
                message=f"Failed to delete task: {str(e)}",
                error_code="DELETE_FAILED"
            ).dict()

    # ========== TAG TOOLS ==========

    def create_tag_tool(
        self,
        name: str,
        color: str = "#6B7280",
        user_id: str = None
    ) -> Dict[str, Any]:
        """Create a new tag"""
        try:
            user_uuid = self._get_user_id(user_id)
            if not user_uuid:
                return ToolResult(
                    success=False,
                    message="User not authenticated",
                    error_code="AUTH_REQUIRED"
                ).dict()

            # Check for duplicates
            existing = self.db_session.exec(
                select(Tag).where(
                    Tag.user_id == user_uuid,
                    Tag.name.ilike(name)
                )
            ).first()

            if existing:
                return ToolResult(
                    success=False,
                    message=f"Tag '{name}' already exists",
                    error_code="DUPLICATE"
                ).dict()

            tag = Tag(
                user_id=user_uuid,
                name=name,
                color=color or "#6B7280"
            )

            self.db_session.add(tag)
            self.db_session.commit()
            self.db_session.refresh(tag)

            # Broadcast live update via WebSocket
            if WEBSOCKET_AVAILABLE and websocket_manager:
                tag_data = {
                    "id": str(tag.id),
                    "name": tag.name,
                    "color": tag.color
                }
                self._broadcast_websocket("tag", "created", tag_data, str(user_uuid))

            return ToolResult(
                success=True,
                message=f"Tag '{name}' created successfully",
                data={
                    "id": str(tag.id),
                    "name": tag.name,
                    "color": tag.color
                }
            ).dict()

        except Exception as e:
            self.db_session.rollback()
            return ToolResult(
                success=False,
                message=f"Failed to create tag: {str(e)}",
                error_code="CREATE_FAILED"
            ).dict()

    def list_tags_tool(self, user_id: str = None) -> Dict[str, Any]:
        """List all tags for user"""
        try:
            user_uuid = self._get_user_id(user_id)
            if not user_uuid:
                return ToolResult(
                    success=False,
                    message="User not authenticated",
                    error_code="AUTH_REQUIRED"
                ).dict()

            tags = self.db_session.exec(
                select(Tag).where(Tag.user_id == user_uuid).order_by(Tag.name)
            ).all()

            tag_list = []
            for tag in tags:
                usage_count = self.db_session.exec(
                    select(TaskTag).where(TaskTag.tag_id == tag.id)
                ).all()

                tag_list.append({
                    "id": str(tag.id),
                    "name": tag.name,
                    "color": tag.color,
                    "usage_count": len(usage_count)
                })

            return ToolResult(
                success=True,
                message=f"Found {len(tag_list)} tags",
                data=tag_list
            ).dict()

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"Failed to list tags: {str(e)}",
                error_code="LIST_FAILED"
            ).dict()

    def assign_tag_to_task_tool(
        self,
        tag_id: str,
        task_id: str,
        user_id: str = None
    ) -> Dict[str, Any]:
        """Assign a tag to a task"""
        try:
            tag_uuid = self._safe_uuid(tag_id)
            task_uuid = self._safe_uuid(task_id)

            if not tag_uuid or not task_uuid:
                return ToolResult(
                    success=False,
                    message="Invalid ID format",
                    error_code="INVALID_ID"
                ).dict()

            tag = self.db_session.get(Tag, tag_uuid)
            task = self.db_session.get(Todo, task_uuid)

            if not tag or not task:
                return ToolResult(
                    success=False,
                    message="Tag or task not found",
                    error_code="NOT_FOUND"
                ).dict()

            user_uuid = self._get_user_id(user_id)
            if user_uuid:
                if task.user_id != user_uuid or tag.user_id != user_uuid:
                    return ToolResult(
                        success=False,
                        message="Access denied",
                        error_code="ACCESS_DENIED"
                    ).dict()

            # Check if already assigned
            existing = self.db_session.exec(
                select(TaskTag).where(
                    TaskTag.task_id == task_uuid,
                    TaskTag.tag_id == tag_uuid
                )
            ).first()

            if existing:
                return ToolResult(
                    success=False,
                    message="Tag already assigned to task",
                    error_code="ALREADY_ASSIGNED"
                ).dict()

            assignment = TaskTag(task_id=task_uuid, tag_id=tag_uuid)
            self.db_session.add(assignment)
            self.db_session.commit()

            # Broadcast live update via WebSocket
            if WEBSOCKET_AVAILABLE and websocket_manager:
                try:
                    task_data = {
                        "id": str(task_id),
                        "tag_id": str(tag_id),
                        "tag_name": tag.name
                    }
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(
                            websocket_manager.broadcast_task_update("tag_assigned", task_data, str(user_uuid))
                        )
                    finally:
                        loop.close()
                except Exception as notify_error:
                    print(f"WebSocket notification error: {notify_error}")

            return ToolResult(
                success=True,
                message=f"Tag '{tag.name}' assigned to task '{task.title}'",
                data={
                    "tag_id": str(tag.id),
                    "task_id": str(task.id)
                }
            ).dict()

        except Exception as e:
            self.db_session.rollback()
            return ToolResult(
                success=False,
                message=f"Failed to assign tag: {str(e)}",
                error_code="ASSIGN_FAILED"
            ).dict()

    def delete_tag_tool(self, tag_id: str, user_id: str = None) -> Dict[str, Any]:
        """Delete a tag"""
        try:
            tag_uuid = self._safe_uuid(tag_id)
            if not tag_uuid:
                return ToolResult(
                    success=False,
                    message="Invalid tag ID",
                    error_code="INVALID_ID"
                ).dict()

            tag = self.db_session.get(Tag, tag_uuid)
            if not tag:
                return ToolResult(
                    success=False,
                    message="Tag not found",
                    error_code="NOT_FOUND"
                ).dict()

            user_uuid = self._get_user_id(user_id)
            if user_uuid and tag.user_id != user_uuid:
                return ToolResult(
                    success=False,
                    message="Access denied",
                    error_code="ACCESS_DENIED"
                ).dict()

            tag_name = tag.name
            tag_data = {"id": str(tag_id), "name": tag_name}
            self.db_session.delete(tag)
            self.db_session.commit()

            # Broadcast live update via WebSocket
            if WEBSOCKET_AVAILABLE and websocket_manager:
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(
                            websocket_manager.broadcast_tag_update("deleted", tag_data, str(user_uuid))
                        )
                    finally:
                        loop.close()
                except Exception as notify_error:
                    print(f"WebSocket notification error: {notify_error}")

            return ToolResult(
                success=True,
                message=f"Tag '{tag_name}' deleted successfully",
                data={"id": str(tag_id)}
            ).dict()

        except Exception as e:
            self.db_session.rollback()
            return ToolResult(
                success=False,
                message=f"Failed to delete tag: {str(e)}",
                error_code="DELETE_FAILED"
            ).dict()

    def unassign_tag_from_task_tool(
        self,
        tag_id: str,
        task_id: str,
        user_id: str = None
    ) -> Dict[str, Any]:
        """Remove a tag from a task"""
        try:
            tag_uuid = self._safe_uuid(tag_id)
            task_uuid = self._safe_uuid(task_id)

            if not tag_uuid or not task_uuid:
                return ToolResult(
                    success=False,
                    message="Invalid ID format",
                    error_code="INVALID_ID"
                ).dict()

            tag = self.db_session.get(Tag, tag_uuid)
            task = self.db_session.get(Todo, task_uuid)

            if not tag or not task:
                return ToolResult(
                    success=False,
                    message="Tag or task not found",
                    error_code="NOT_FOUND"
                ).dict()

            user_uuid = self._get_user_id(user_id)
            if user_uuid:
                if task.user_id != user_uuid or tag.user_id != user_uuid:
                    return ToolResult(
                        success=False,
                        message="Access denied",
                        error_code="ACCESS_DENIED"
                    ).dict()

            # Find the assignment
            assignment = self.db_session.exec(
                select(TaskTag).where(
                    TaskTag.task_id == task_uuid,
                    TaskTag.tag_id == tag_uuid
                )
            ).first()

            if not assignment:
                return ToolResult(
                    success=False,
                    message="Tag assignment not found",
                    error_code="NOT_FOUND"
                ).dict()

            self.db_session.delete(assignment)
            self.db_session.commit()

            # Broadcast live update via WebSocket
            if WEBSOCKET_AVAILABLE and websocket_manager:
                try:
                    task_data = {
                        "id": str(task_id),
                        "tag_id": str(tag_id),
                        "tag_name": tag.name
                    }
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(
                            websocket_manager.broadcast_task_update("tag_removed", task_data, str(user_uuid))
                        )
                    finally:
                        loop.close()
                except Exception as notify_error:
                    print(f"WebSocket notification error: {notify_error}")

            return ToolResult(
                success=True,
                message="Tag removed from task successfully",
                data={
                    "tag_id": str(tag.id),
                    "task_id": str(task.id)
                }
            ).dict()

        except Exception as e:
            self.db_session.rollback()
            return ToolResult(
                success=False,
                message=f"Failed to unassign tag: {str(e)}",
                error_code="UNASSIGN_FAILED"
            ).dict()

    # ========== REMINDER TOOLS ==========

    def create_reminder_tool(
        self,
        task_id: str,
        user_id: str = None,
        timing_minutes: int = 0,
        timing_days: Optional[int] = None,
        delivery_channel: str = "in_app"
    ) -> Dict[str, Any]:
        """Create a reminder for a task"""
        try:
            user_uuid = self._get_user_id(user_id)
            if not user_uuid:
                return ToolResult(
                    success=False,
                    message="User not authenticated",
                    error_code="AUTH_REQUIRED"
                ).dict()

            task_uuid = self._safe_uuid(task_id)
            if not task_uuid:
                return ToolResult(
                    success=False,
                    message="Invalid task ID",
                    error_code="INVALID_ID"
                ).dict()

            task = self.db_session.get(Todo, task_uuid)
            if not task:
                return ToolResult(
                    success=False,
                    message="Task not found",
                    error_code="NOT_FOUND"
                ).dict()

            if not task.due_date:
                return ToolResult(
                    success=False,
                    message="Task must have a due date to set a reminder",
                    error_code="INVALID_ID"
                ).dict()

            # Calculate scheduled time
            scheduled_time = self._calculate_reminder_time(
                task.due_date,
                timing_minutes,
                timing_days
            )

            reminder = Reminder(
                task_id=task_uuid,
                timing_minutes=timing_minutes,
                timing_days=timing_days,
                delivery_channel=delivery_channel or "in_app",
                scheduled_time=scheduled_time,
                status="pending"
            )

            self.db_session.add(reminder)
            self.db_session.commit()
            self.db_session.refresh(reminder)

            # Broadcast live update via WebSocket
            if WEBSOCKET_AVAILABLE and websocket_manager:
                try:
                    reminder_data = {
                        "id": str(reminder.id),
                        "task_id": str(task.id),
                        "task_title": task.title,
                        "scheduled_time": reminder.scheduled_time.isoformat(),
                        "timing_minutes": reminder.timing_minutes,
                        "timing_days": reminder.timing_days
                    }
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(
                            websocket_manager.broadcast_reminder_update("created", reminder_data, str(user_uuid))
                        )
                    finally:
                        loop.close()
                except Exception as notify_error:
                    print(f"WebSocket notification error: {notify_error}")

            return ToolResult(
                success=True,
                message=f"Reminder set for task '{task.title}'",
                data={
                    "id": str(reminder.id),
                    "task_id": str(task.id),
                    "scheduled_time": reminder.scheduled_time.isoformat(),
                    "timing_minutes": reminder.timing_minutes,
                    "timing_days": reminder.timing_days
                }
            ).dict()

        except Exception as e:
            self.db_session.rollback()
            return ToolResult(
                success=False,
                message=f"Failed to create reminder: {str(e)}",
                error_code="CREATE_FAILED"
            ).dict()

    def list_reminders_tool(self, user_id: str = None) -> Dict[str, Any]:
        """List all reminders for user"""
        try:
            user_uuid = self._get_user_id(user_id)
            if not user_uuid:
                return ToolResult(
                    success=False,
                    message="User not authenticated",
                    error_code="AUTH_REQUIRED"
                ).dict()

            # Get all tasks for user
            user_tasks_statement = select(Todo.id).where(Todo.user_id == user_uuid)
            user_task_ids = self.db_session.exec(user_tasks_statement).all()

            if not user_task_ids:
                return ToolResult(
                    success=True,
                    message="No reminders found",
                    data=[]
                ).dict()

            # Get reminders for user's tasks
            statement = select(Reminder).where(Reminder.task_id.in_(user_task_ids))
            reminders = self.db_session.exec(statement.order_by(Reminder.scheduled_time)).all()

            reminder_list = []
            for reminder in reminders:
                task = self.db_session.get(Todo, reminder.task_id)
                reminder_list.append({
                    "id": str(reminder.id),
                    "task_id": str(reminder.task_id),
                    "task_title": task.title if task else "Unknown",
                    "timing_minutes": reminder.timing_minutes,
                    "timing_days": reminder.timing_days,
                    "scheduled_time": reminder.scheduled_time.isoformat(),
                    "status": reminder.status,
                    "delivery_channel": reminder.delivery_channel
                })

            return ToolResult(
                success=True,
                message=f"Found {len(reminder_list)} reminders",
                data=reminder_list
            ).dict()

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"Failed to list reminders: {str(e)}",
                error_code="LIST_FAILED"
            ).dict()

    def delete_reminder_tool(self, reminder_id: str, user_id: str = None) -> Dict[str, Any]:
        """Delete/cancel a reminder"""
        try:
            user_uuid = self._get_user_id(user_id)
            if not user_uuid:
                return ToolResult(
                    success=False,
                    message="User not authenticated",
                    error_code="AUTH_REQUIRED"
                ).dict()

            reminder_uuid = self._safe_uuid(reminder_id)
            if not reminder_uuid:
                return ToolResult(
                    success=False,
                    message="Invalid reminder ID",
                    error_code="INVALID_ID"
                ).dict()

            reminder = self.db_session.get(Reminder, reminder_uuid)
            if not reminder:
                return ToolResult(
                    success=False,
                    message="Reminder not found",
                    error_code="NOT_FOUND"
                ).dict()

            # Verify ownership through task
            task = self.db_session.get(Todo, reminder.task_id)
            if not task or task.user_id != user_uuid:
                return ToolResult(
                    success=False,
                    message="Access denied",
                    error_code="ACCESS_DENIED"
                ).dict()

            self.db_session.delete(reminder)
            self.db_session.commit()

            # Broadcast live update via WebSocket
            if WEBSOCKET_AVAILABLE and websocket_manager:
                try:
                    reminder_data = {
                        "id": str(reminder_id),
                        "task_id": str(reminder.task_id),
                        "task_title": task.title
                    }
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(
                            websocket_manager.broadcast_reminder_update("deleted", reminder_data, str(user_uuid))
                        )
                    finally:
                        loop.close()
                except Exception as notify_error:
                    print(f"WebSocket notification error: {notify_error}")

            return ToolResult(
                success=True,
                message="Reminder deleted successfully",
                data={"id": str(reminder_id)}
            ).dict()

        except Exception as e:
            self.db_session.rollback()
            return ToolResult(
                success=False,
                message=f"Failed to delete reminder: {str(e)}",
                error_code="DELETE_FAILED"
            ).dict()

    # ========== SEARCH TOOLS ==========

    def search_tasks_tool(
        self,
        query: str,
        user_id: str = None,
        priority: str = None,
        status: str = None,
        tag_id: str = None,
        due_date_from: str = None,
        due_date_to: str = None
    ) -> Dict[str, Any]:
        """Search tasks by text and filters"""
        try:
            user_uuid = self._get_user_id(user_id)
            if not user_uuid:
                return ToolResult(
                    success=False,
                    message="User not authenticated",
                    error_code="AUTH_REQUIRED"
                ).dict()

            # Build search query
            from sqlalchemy import text
            search_sql = text("""
                SELECT t.*
                FROM todos t
                WHERE t.user_id = :user_id
                  AND (
                    t.title ILIKE '%' || :query || '%' OR
                    t.description ILIKE '%' || :query || '%'
                  )
                  AND (:priority IS NULL OR t.priority = :priority)
                  AND (:status IS NULL OR t.is_completed = :status)
                  AND (:tag_id IS NULL OR t.id IN (
                      SELECT task_id FROM task_tags WHERE tag_id = :tag_id::uuid
                  ))
                  AND (:due_date_from IS NULL OR t.due_date >= :due_date_from)
                  AND (:due_date_to IS NULL OR t.due_date <= :due_date_to)
                ORDER BY t.created_at DESC
                LIMIT 50
            """)

            sql_status = None
            if status == "completed":
                sql_status = True
            elif status == "pending":
                sql_status = False

            # Parse dates
            parsed_due_date_from = None
            if due_date_from:
                try:
                    parsed_due_date_from = datetime.fromisoformat(due_date_from.replace('Z', '+00:00'))
                except:
                    pass

            parsed_due_date_to = None
            if due_date_to:
                try:
                    parsed_due_date_to = datetime.fromisoformat(due_date_to.replace('Z', '+00:00'))
                except:
                    pass

            results = self.db_session.execute(
                search_sql,
                {
                    'user_id': user_uuid,
                    'query': query,
                    'priority': priority,
                    'status': sql_status,
                    'tag_id': tag_id,
                    'due_date_from': parsed_due_date_from,
                    'due_date_to': parsed_due_date_to
                }
            )

            tasks = []
            for row in results:
                tasks.append({
                    "id": str(row.id),
                    "title": row.title,
                    "description": row.description,
                    "completed": row.is_completed,
                    "priority": row.priority,
                    "due_date": row.due_date.isoformat() if row.due_date else None
                })

            # Broadcast search results via WebSocket
            if WEBSOCKET_AVAILABLE and websocket_manager:
                try:
                    search_data = {
                        "query": query,
                        "count": len(tasks),
                        "tasks": tasks
                    }
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(
                            websocket_manager.broadcast_search_update(search_data, str(user_uuid))
                        )
                    finally:
                        loop.close()
                except Exception as notify_error:
                    print(f"WebSocket notification error: {notify_error}")

            return ToolResult(
                success=True,
                message=f"Found {len(tasks)} tasks matching '{query}'",
                data=tasks
            ).dict()

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"Search failed: {str(e)}",
                error_code="SEARCH_FAILED"
            ).dict()

    def filter_tasks_tool(
        self,
        user_id: str,
        priority: str = None,
        status: str = None,
        tag_id: str = None,
        due_date_from: str = None,
        due_date_to: str = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Filter tasks without text search"""
        try:
            user_uuid = self._get_user_id(user_id)
            if not user_uuid:
                return ToolResult(
                    success=False,
                    message="User not authenticated",
                    error_code="AUTH_REQUIRED"
                ).dict()

            # Build query
            statement = select(Todo).where(Todo.user_id == user_uuid)

            # Apply filters
            if status == "completed":
                statement = statement.where(Todo.is_completed == True)
            elif status == "pending":
                statement = statement.where(Todo.is_completed == False)

            if priority:
                statement = statement.where(Todo.priority == priority)

            if tag_id:
                tag_uuid = self._safe_uuid(tag_id)
                if tag_uuid:
                    tag_subquery = select(TaskTag.task_id).where(TaskTag.tag_id == tag_uuid)
                    statement = statement.where(Todo.id.in_(tag_subquery))

            # Parse dates
            if due_date_from:
                try:
                    due_date_from_dt = datetime.fromisoformat(due_date_from.replace('Z', '+00:00'))
                    statement = statement.where(Todo.due_date >= due_date_from_dt)
                except:
                    pass

            if due_date_to:
                try:
                    due_date_to_dt = datetime.fromisoformat(due_date_to.replace('Z', '+00:00'))
                    statement = statement.where(Todo.due_date <= due_date_to_dt)
                except:
                    pass

            # Apply limit
            statement = statement.limit(limit)

            tasks = self.db_session.exec(statement).all()

            task_list = []
            for task in tasks:
                task_tags = self.db_session.exec(
                    select(TaskTag).where(TaskTag.task_id == task.id)
                ).all()

                task_list.append({
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "completed": task.is_completed,
                    "priority": task.priority,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "tags": [
                        {"id": str(tt.tag.id), "name": tt.tag.name, "color": tt.tag.color}
                        for tt in task_tags
                    ],
                    "created_at": task.created_at.isoformat()
                })

            return ToolResult(
                success=True,
                message=f"Found {len(task_list)} tasks",
                data=task_list
            ).dict()

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"Failed to filter tasks: {str(e)}",
                error_code="LIST_FAILED"
            ).dict()

    # ========== TOOLS SPEC ==========

    def get_tools_spec(self) -> List[Dict[str, Any]]:
        """Return comprehensive tool specifications"""
        return [
            # Task Operations
            {
                "type": "function",
                "function": {
                    "name": "create_task",
                    "description": "Create a new task with title, description, priority, and due date",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Task title (required)"},
                            "description": {"type": "string", "description": "Task description (optional)"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"], "description": "Task priority"},
                            "due_date": {"type": "string", "description": "Due date - can be natural language like 'tomorrow', 'next Monday', 'in 2 days', or ISO format"},
                            "time_str": {"type": "string", "description": "Time specification - can be 'morning' (9AM), 'afternoon' (2PM), 'evening' (6PM), 'night' (9PM), or specific time like '9pm', '2:30 PM'"},
                            "user_id": {"type": "string", "description": "User ID (auto-injected)"}
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "List tasks with optional filters for status, priority, and tags",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "enum": ["all", "completed", "pending"], "description": "Filter by status"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"], "description": "Filter by priority"},
                            "tag_id": {"type": "string", "description": "Filter by tag ID"},
                            "limit": {"type": "integer", "description": "Maximum results (default: 50)"},
                            "user_id": {"type": "string", "description": "User ID (auto-injected)"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update task title, description, priority, due date, or completion status",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string", "description": "Task ID to update"},
                            "title": {"type": "string", "description": "New title"},
                            "description": {"type": "string", "description": "New description"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"], "description": "New priority"},
                            "due_date": {"type": "string", "description": "New due date"},
                            "completed": {"type": "boolean", "description": "Completion status"},
                            "user_id": {"type": "string", "description": "User ID (auto-injected)"}
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Mark a task as completed",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string", "description": "Task ID to complete"},
                            "user_id": {"type": "string", "description": "User ID (auto-injected)"}
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Delete a task permanently",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string", "description": "Task ID to delete"},
                            "user_id": {"type": "string", "description": "User ID (auto-injected)"}
                        },
                        "required": ["task_id"]
                    }
                }
            },
            # Tag Operations
            {
                "type": "function",
                "function": {
                    "name": "create_tag",
                    "description": "Create a new tag with name and color",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Tag name"},
                            "color": {"type": "string", "description": "Hex color code (e.g., #FF0000)"},
                            "user_id": {"type": "string", "description": "User ID (auto-injected)"}
                        },
                        "required": ["name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tags",
                    "description": "List all tags for the user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "User ID (auto-injected)"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "assign_tag_to_task",
                    "description": "Assign a tag to a task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "tag_id": {"type": "string", "description": "Tag ID"},
                            "task_id": {"type": "string", "description": "Task ID"},
                            "user_id": {"type": "string", "description": "User ID (auto-injected)"}
                        },
                        "required": ["tag_id", "task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_tag",
                    "description": "Delete a tag (removes from all tasks)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "tag_id": {"type": "string", "description": "Tag ID to delete"},
                            "user_id": {"type": "string", "description": "User ID (auto-injected)"}
                        },
                        "required": ["tag_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "unassign_tag_from_task",
                    "description": "Remove a tag from a task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "tag_id": {"type": "string", "description": "Tag ID to remove"},
                            "task_id": {"type": "string", "description": "Task ID to remove tag from"},
                            "user_id": {"type": "string", "description": "User ID (auto-injected)"}
                        },
                        "required": ["tag_id", "task_id"]
                    }
                }
            },
            # Reminder Operations
            {
                "type": "function",
                "function": {
                    "name": "create_reminder",
                    "description": "Create a reminder for a task with a due date",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string", "description": "Task ID to remind about"},
                            "timing_minutes": {"type": "integer", "description": "Minutes before due date to remind (default: 0)"},
                            "timing_days": {"type": "integer", "description": "Days before due date to remind (optional)"},
                            "delivery_channel": {"type": "string", "enum": ["in_app", "email", "web_push"], "description": "How to deliver reminder"},
                            "user_id": {"type": "string", "description": "User ID (auto-injected)"}
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_reminders",
                    "description": "List all reminders for the user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "User ID (auto-injected)"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_reminder",
                    "description": "Delete/cancel a reminder",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "reminder_id": {"type": "string", "description": "Reminder ID to delete"},
                            "user_id": {"type": "string", "description": "User ID (auto-injected)"}
                        },
                        "required": ["reminder_id"]
                    }
                }
            },
            # Search Operations
            {
                "type": "function",
                "function": {
                    "name": "search_tasks",
                    "description": "Search tasks by text query with optional filters",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query (searches title and description)"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"], "description": "Filter by priority"},
                            "status": {"type": "string", "enum": ["all", "completed", "pending"], "description": "Filter by status"},
                            "tag_id": {"type": "string", "description": "Filter by tag ID"},
                            "due_date_from": {"type": "string", "description": "Filter by due date from (ISO format)"},
                            "due_date_to": {"type": "string", "description": "Filter by due date to (ISO format)"},
                            "user_id": {"type": "string", "description": "User ID (auto-injected)"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "filter_tasks",
                    "description": "Filter tasks by priority, status, tag, or due date range",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"], "description": "Filter by priority"},
                            "status": {"type": "string", "enum": ["all", "completed", "pending"], "description": "Filter by status"},
                            "tag_id": {"type": "string", "description": "Filter by tag ID"},
                            "due_date_from": {"type": "string", "description": "Filter by due date from (ISO format)"},
                            "due_date_to": {"type": "string", "description": "Filter by due date to (ISO format)"},
                            "limit": {"type": "integer", "description": "Maximum results (default: 50)"},
                            "user_id": {"type": "string", "description": "User ID (auto-injected)"}
                        }
                    }
                }
            }
        ]

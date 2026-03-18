from agents import Agent, Runner, function_tool, SQLiteSession
import requests
from connection import config
from openai.types.responses import ResponseTextDeltaEvent
import asyncio
from pydantic import BaseModel
from dotenv import load_dotenv
from pydantic import ValidationError
from sqlmodel import SQLModel, Field, create_engine, Session as SQLSession, select
from typing import Optional
import uuid
from datetime import datetime
import os
import sys

# Add the parent directory to the path to access the existing models
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.models.todo import Todo
from app.models.user import User
from app.database.session import engine

# Import notification functions
from notification import (
    notify_task_created_sync,
    notify_task_updated_sync,
    notify_task_completed_sync,
    notify_task_deleted_sync
)

load_dotenv()


# session = SQLiteSession("my_first_conversation")  # Moved to be created per request




@function_tool
def task_creation(title: str, description: Optional[str] = None, user_id: str = None) -> dict:
    """Create a new task in the database."""
    try:
        # Convert user_id to UUID
        user_uuid = uuid.UUID(user_id)

        # Create a new task
        new_task = Todo(
            title=title,
            description=description or "",
            is_completed=False,
            user_id=user_uuid
        )

        # Use a database session to save the task
        with SQLSession(engine) as db_session:
            db_session.add(new_task)
            db_session.commit()
            db_session.refresh(new_task)

        # Prepare task data for notification
        task_data = {
            "task_id": str(new_task.id),
            "title": new_task.title,
            "description": new_task.description,
            "completed": new_task.is_completed,
            "created_at": new_task.created_at.isoformat() if new_task.created_at else None,
            "updated_at": new_task.updated_at.isoformat() if new_task.updated_at else None
        }

        # Send notification about the new task
        try:
            notify_task_created_sync(user_id, task_data)
        except Exception as notify_error:
            print(f"Notification error: {notify_error}")

        return {
            "success": True,
            "message": f"Task '{title}' created successfully",
            "task_id": str(new_task.id),
            "title": new_task.title,
            "description": new_task.description,
            "completed": new_task.is_completed
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to create task: {str(e)}"
        }


@function_tool
def task_update(task_id: str = None, title: str = None, new_title: Optional[str] = None, description: Optional[str] = None, completed: Optional[bool] = None, user_id: str = None) -> dict:
    """Update an existing task in the database by ID or title."""
    try:
        with SQLSession(engine) as db_session:
            task = None

            # If task_id is provided, use it directly
            if task_id:
                try:
                    task_uuid = uuid.UUID(task_id)
                    task = db_session.get(Todo, task_uuid)
                except ValueError:
                    # If not a valid UUID, treat as title and search by user_id
                    if user_id:
                        user_uuid = uuid.UUID(user_id)
                        statement = select(Todo).where(
                            (Todo.title == task_id) &
                            (Todo.user_id == user_uuid)
                        )
                        tasks = db_session.exec(statement).all()
                        if tasks:
                            task = tasks[0]
                            task_id = str(task.id)

            # If title is provided, search for the task by title for the user
            elif title and user_id:
                user_uuid = uuid.UUID(user_id)
                # Find task by title and user_id
                statement = select(Todo).where(
                    (Todo.title == title) &
                    (Todo.user_id == user_uuid)
                )
                tasks = db_session.exec(statement).all()

                if tasks:
                    # Take the first matching task
                    task = tasks[0]
                    task_id = str(task.id)

            if not task:
                return {
                    "success": False,
                    "message": f"Task not found (ID: {task_id}, Title: {title or task_id})"
                }

            # Update the task properties if provided
            original_title = task.title
            if new_title is not None:
                task.title = new_title
            if description is not None:
                task.description = description
            if completed is not None:
                task.is_completed = completed

            db_session.add(task)
            db_session.commit()
            db_session.refresh(task)

        # Prepare task data for notification
        task_data = {
            "task_id": str(task.id),
            "title": task.title,
            "description": task.description,
            "completed": task.is_completed,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None
        }

        # Send notification about the task update
        try:
            notify_task_updated_sync(user_id, task_data)
        except Exception as notify_error:
            print(f"Notification error: {notify_error}")

        return {
            "success": True,
            "message": f"Task '{original_title}' updated successfully",
            "task_id": str(task.id),
            "title": task.title,
            "description": task.description,
            "completed": task.is_completed
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to update task: {str(e)}"
        }


@function_tool
def task_completion(task_id: str = None, title: str = None, user_id: str = None) -> dict:
    """Mark a task as completed in the database by ID or title."""
    try:
        with SQLSession(engine) as db_session:
            task = None

            # If task_id is provided, try to use it as UUID, otherwise treat as title
            if task_id:
                try:
                    # First try treating as UUID
                    task_uuid = uuid.UUID(task_id)
                    task = db_session.get(Todo, task_uuid)
                except ValueError:
                    # If not a valid UUID, treat as title and search by user_id
                    if user_id:
                        user_uuid = uuid.UUID(user_id)
                        # Find task by title and user_id
                        statement = select(Todo).where(
                            (Todo.title == task_id) &
                            (Todo.user_id == user_uuid)
                        )
                        tasks = db_session.exec(statement).all()

                        if tasks:
                            # Take the first matching task
                            task = tasks[0]
                            task_id = str(task.id)
                    else:
                        # If no user_id provided, we can't search by title
                        pass

            # If title is provided, search for the task by title for the user
            elif title and user_id:
                user_uuid = uuid.UUID(user_id)
                # Find task by title and user_id
                statement = select(Todo).where(
                    (Todo.title == title) &
                    (Todo.user_id == user_uuid)
                )
                tasks = db_session.exec(statement).all()

                if tasks:
                    # Take the first matching task
                    task = tasks[0]
                    task_id = str(task.id)

            if not task:
                return {
                    "success": False,
                    "message": f"Task not found (ID: {task_id}, Title: {title or task_id})"
                }

            task.is_completed = True
            db_session.add(task)
            db_session.commit()
            db_session.refresh(task)

        # Prepare task data for notification
        task_data = {
            "task_id": str(task.id),
            "title": task.title,
            "description": task.description,
            "completed": task.is_completed,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None
        }

        # Send notification about the task completion
        try:
            notify_task_completed_sync(user_id, task_data)
        except Exception as notify_error:
            print(f"Notification error: {notify_error}")

        return {
            "success": True,
            "message": f"Task '{task.title}' marked as completed",
            "task_id": str(task.id),
            "title": task.title,
            "completed": task.is_completed
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to complete task: {str(e)}"
        }


@function_tool
def task_deletion(task_id: str = None, title: str = None, user_id: str = None) -> dict:
    """Delete a task from the database by ID or title."""
    try:
        with SQLSession(engine) as db_session:
            task = None

            # If task_id is provided, use it directly
            if task_id:
                try:
                    task_uuid = uuid.UUID(task_id)
                    task = db_session.get(Todo, task_uuid)
                except ValueError:
                    # If not a valid UUID, treat as title and search by user_id
                    if user_id:
                        user_uuid = uuid.UUID(user_id)
                        # Find task by title and user_id
                        statement = select(Todo).where(
                            (Todo.title == task_id) &
                            (Todo.user_id == user_uuid)
                        )
                        tasks = db_session.exec(statement).all()
                        if tasks:
                            # Take the first matching task
                            task = tasks[0]
                            task_id = str(task.id)

            # If title is provided, search for the task by title for the user
            elif title and user_id:
                user_uuid = uuid.UUID(user_id)
                # Find task by title and user_id
                statement = select(Todo).where(
                    (Todo.title == title) &
                    (Todo.user_id == user_uuid)
                )
                tasks = db_session.exec(statement).all()

                if tasks:
                    # Take the first matching task
                    task = tasks[0]
                    task_id = str(task.id)

            if not task:
                return {
                    "success": False,
                    "message": f"Task not found (ID: {task_id}, Title: {title or task_id})"
                }

            # Prepare task data for notification (before deletion)
            task_data = {
                "task_id": str(task.id),
                "title": task.title,
                "description": task.description,
                "completed": task.is_completed,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None
            }

            db_session.delete(task)
            db_session.commit()

        # Send notification about the task deletion
        try:
            notify_task_deleted_sync(user_id, task_data)
        except Exception as notify_error:
            print(f"Notification error: {notify_error}")

        return {
            "success": True,
            "message": f"Task '{task.title}' deleted successfully",
            "task_id": str(task.id)
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to delete task: {str(e)}"
        }


@function_tool
def task_list(user_id: str) -> dict:
    """List all tasks for a specific user."""
    try:
        # Convert user_id to UUID
        user_uuid = uuid.UUID(user_id)

        # Query tasks for the user
        with SQLSession(engine) as db_session:
            statement = select(Todo).where(Todo.user_id == user_uuid)
            tasks = db_session.exec(statement).all()

            task_list = []
            for task in tasks:
                task_list.append({
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "completed": task.is_completed,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "updated_at": task.updated_at.isoformat() if task.updated_at else None
                })

        return {
            "success": True,
            "message": f"Found {len(task_list)} tasks for user",
            "tasks": task_list
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to list tasks: {str(e)}"
        }


task_deletion_agent = Agent(
    name="task_deletion_agent",
    instructions="You are a helpful task deletion agent. Use the task_deletion tool to remove tasks from the database. You can delete tasks either by providing the specific task_id, or by providing both the task title and user_id to identify the task by name.",
    tools=[task_deletion]
)


task_completion_agent = Agent(
    name="task_completion_agent",
    instructions="You are a helpful task completion agent. Use the task_completion tool to mark tasks as completed. You can complete tasks either by providing the specific task_id, or by providing both the task title and user_id to identify the task by name.",
    tools=[task_completion]
)

task_update_agent = Agent(
    name="task_update_agent",
    instructions="You are a helpful task updating agent. Use the task_update tool to modify existing tasks. You can update tasks either by providing the specific task_id, or by providing the current task title and user_id to identify the task by name.",
    tools=[task_update]
)

task_creation_agent = Agent(
    name="task_creation_agent",
    instructions="You are a helpful task creation agent. Use the task_creation tool to create new tasks in the database.",
    tools=[task_creation]
)

task_list_agent = Agent(
    name="task_list_agent",
    instructions="You are a helpful task listing agent. Use the task_list tool to retrieve tasks for a user.",
    tools=[task_list]
)

triage_agent = Agent(
    name="triage_agent",
    instructions="You are a helpful triage agent. Determine what the user wants to do with their tasks and delegate to the appropriate agent. When users refer to tasks by name/title, you can pass both the task title and user_id to the appropriate agent. Available agents: task_creation_agent for creating tasks, task_list_agent for listing tasks, task_update_agent for updating tasks (can update by title), task_completion_agent for completing tasks (can complete by title), or task_deletion_agent for deleting tasks (can delete by title).",
    handoffs=[task_creation_agent, task_list_agent, task_update_agent, task_completion_agent, task_deletion_agent]
)


async def main():
    # Run the agent in an interactive demo loop
    while True:
        user_input = input("Chat something (or 'quit' to exit): ")

        if user_input.lower() == 'quit':
            break

        result = Runner.run_streamed(
            triage_agent,
            user_input,
            run_config=config,
            session=session
        )

        try:
            async for event in result.stream_events():
                if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                    print(event.data.delta, end="", flush=True)
            print()  # New line after response
        except ValidationError as validation_error:
            print("Validation error:", validation_error)
        except Exception as e:
            print("An unhandled error occurred:", e)


if __name__ == "__main__":
    asyncio.run(main())
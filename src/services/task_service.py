"""
TaskService for the Todo App Core Functionality.
Handles business logic for task operations.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from typing import List, Optional
from models.task import Task, TaskList


class TaskService:
    """Service layer for task operations."""

    def __init__(self):
        """Initialize the TaskService with an empty TaskList."""
        self.task_list = TaskList()

    def add_task(self, title: str, description: str = "") -> Optional[Task]:
        """
        Add a new task.

        Args:
            title: Title of the task to add
            description: Description of the task to add (optional)

        Returns:
            The newly created Task if successful, None otherwise
        """
        if not title or not title.strip():
            return None
        return self.task_list.add_task(title.strip(), description.strip() if description else "")

    def get_all_tasks(self) -> List[Task]:
        """
        Get all tasks.

        Returns:
            List of all tasks
        """
        return self.task_list.get_all_tasks()

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by ID.

        Args:
            task_id: ID of the task to delete

        Returns:
            True if task was deleted, False if task not found
        """
        return self.task_list.delete_task(task_id)

    def update_task(self, task_id: int, title: str = None, description: str = None) -> bool:
        """
        Update a task's title and/or description.

        Args:
            task_id: ID of the task to update
            title: New title for the task (optional)
            description: New description for the task (optional)

        Returns:
            True if task was updated, False if task not found
        """
        # Only validate title if it's being updated
        if title is not None and (not title or not title.strip()):
            return False
        if title is not None:
            title = title.strip()
        if description is not None:
            description = description.strip()
        return self.task_list.update_task(task_id, title=title, description=description)

    def mark_complete(self, task_id: int) -> bool:
        """
        Mark a task as complete.

        Args:
            task_id: ID of the task to mark complete

        Returns:
            True if task was marked complete, False if task not found
        """
        return self.task_list.mark_complete(task_id)

    def mark_incomplete(self, task_id: int) -> bool:
        """
        Mark a task as incomplete.

        Args:
            task_id: ID of the task to mark incomplete

        Returns:
            True if task was marked incomplete, False if task not found
        """
        return self.task_list.mark_incomplete(task_id)

    def get_task(self, task_id: int) -> Optional[Task]:
        """
        Get a task by ID.

        Args:
            task_id: ID of the task to retrieve

        Returns:
            The Task if found, None otherwise
        """
        return self.task_list.get_task(task_id)
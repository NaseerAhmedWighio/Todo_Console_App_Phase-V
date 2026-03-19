"""
Task and TaskList models for the Todo App Core Functionality.
"""
from typing import List, Optional
from datetime import datetime


class Task:
    """Represents a single todo task."""

    def __init__(self, task_id: int, title: str, description: str = "", completed: bool = False):
        """
        Initialize a Task.

        Args:
            task_id: Unique identifier for the task
            title: Title of the task
            description: Description of the task (optional)
            completed: Whether the task is completed (default: False)
        """
        self.id = task_id
        self.title = title
        self.description = description
        self.completed = completed
        self.created_at = datetime.now()

    def __str__(self) -> str:
        """String representation of the task."""
        status = "Complete" if self.completed else "Incomplete"
        if self.description:
            return f"{self.id}. {self.title} - {self.description} [{status}]"
        else:
            return f"{self.id}. {self.title} [{status}]"

    def to_dict(self) -> dict:
        """Convert task to dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at.isoformat()
        }


class TaskList:
    """Manages a collection of tasks in memory."""

    def __init__(self):
        """Initialize an empty task list."""
        self._tasks: List[Task] = []
        self._next_id = 1

    def add_task(self, title: str, description: str = "") -> Task:
        """
        Add a new task to the list.

        Args:
            title: Title of the task to add
            description: Description of the task to add (optional)

        Returns:
            The newly created Task
        """
        task = Task(self._next_id, title, description, False)
        self._tasks.append(task)
        self._next_id += 1
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        """
        Get a task by its ID.

        Args:
            task_id: ID of the task to retrieve

        Returns:
            The Task if found, None otherwise
        """
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    def get_all_tasks(self) -> List[Task]:
        """
        Get all tasks in the list.

        Returns:
            List of all tasks
        """
        return self._tasks.copy()

    def update_task(self, task_id: int, title: str = None, description: str = None, completed: bool = None) -> bool:
        """
        Update a task's title, description, or completion status.

        Args:
            task_id: ID of the task to update
            title: New title (optional)
            description: New description (optional)
            completed: New completion status (optional)

        Returns:
            True if task was updated, False if task not found
        """
        task = self.get_task(task_id)
        if task:
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if completed is not None:
                task.completed = completed
            return True
        return False

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by its ID.

        Args:
            task_id: ID of the task to delete

        Returns:
            True if task was deleted, False if task not found
        """
        task = self.get_task(task_id)
        if task:
            self._tasks.remove(task)
            return True
        return False

    def mark_complete(self, task_id: int) -> bool:
        """
        Mark a task as complete.

        Args:
            task_id: ID of the task to mark complete

        Returns:
            True if task was marked complete, False if task not found
        """
        return self.update_task(task_id, completed=True)

    def mark_incomplete(self, task_id: int) -> bool:
        """
        Mark a task as incomplete.

        Args:
            task_id: ID of the task to mark incomplete

        Returns:
            True if task was marked incomplete, False if task not found
        """
        return self.update_task(task_id, completed=False)

    def clear_completed(self) -> int:
        """
        Remove all completed tasks.

        Returns:
            Number of tasks removed
        """
        initial_count = len(self._tasks)
        self._tasks = [task for task in self._tasks if not task.completed]
        return initial_count - len(self._tasks)
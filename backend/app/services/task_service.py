"""
Task Service
Business logic for task operations including filtering and sorting
"""

from typing import List, Optional
from sqlmodel import Session, select, col
from datetime import datetime
import uuid

from ..models.todo import Todo
from ..models.event import DomainEvent


class TaskService:
    """Service for task operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_tasks(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[bool] = None,
        priority: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> List[Todo]:
        """
        Get tasks with filtering and sorting
        
        Args:
            user_id: ID of the user
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            status: Filter by completion status (True=completed, False=pending)
            priority: Filter by priority level
            sort_by: Field to sort by (created_at, updated_at, due_date, priority, title)
            sort_order: Sort order (asc or desc)
            
        Returns:
            List of Todo items
        """
        statement = select(Todo).where(Todo.user_id == user_id)
        
        # Apply status filter
        if status is not None:
            statement = statement.where(Todo.is_completed == status)
        
        # Apply priority filter
        if priority is not None:
            statement = statement.where(Todo.priority == priority)
        
        # Apply sorting
        if sort_by == "due_date":
            statement = statement.order_by(col(Todo.due_date).asc() if sort_order == "asc" else col(Todo.due_date).desc())
        elif sort_by == "priority":
            # Custom priority ordering: urgent > high > medium > low
            priority_case = self._get_priority_case(sort_order)
            statement = statement.order_by(priority_case)
        elif sort_by == "created_at":
            statement = statement.order_by(col(Todo.created_at).asc() if sort_order == "asc" else col(Todo.created_at).desc())
        elif sort_by == "updated_at":
            statement = statement.order_by(col(Todo.updated_at).asc() if sort_order == "asc" else col(Todo.updated_at).desc())
        elif sort_by == "title":
            statement = statement.order_by(col(Todo.title).asc() if sort_order == "asc" else col(Todo.title).desc())
        
        # Apply pagination
        statement = statement.offset(skip).limit(limit)
        
        return self.session.exec(statement).all()
    
    def _get_priority_case(self, sort_order: str):
        """
        Create CASE expression for priority sorting
        
        Args:
            sort_order: asc or desc
            
        Returns:
            CASE expression for priority ordering
        """
        # Priority values: urgent=1, high=2, medium=3, low=4
        if sort_order == "asc":
            # Urgent first
            return col(Todo.priority).case(
                [("urgent", 1), ("high", 2), ("medium", 3), ("low", 4)],
                else_=5
            )
        else:
            # Low first (reverse)
            return col(Todo.priority).case(
                [("urgent", 4), ("high", 3), ("medium", 2), ("low", 1)],
                else_=0
            )
    
    def get_task_by_id(self, task_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Todo]:
        """
        Get a single task by ID
        
        Args:
            task_id: ID of the task
            user_id: ID of the user (for authorization)
            
        Returns:
            Todo item or None
        """
        task = self.session.get(Todo, task_id)
        if task and task.user_id != user_id:
            return None
        return task
    
    def create_task(self, user_id: uuid.UUID, task_data: dict) -> Todo:
        """
        Create a new task
        
        Args:
            user_id: ID of the user
            task_data: Task data dictionary
            
        Returns:
            Created Todo item
        """
        task = Todo(**task_data, user_id=user_id)
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task
    
    def update_task(self, task_id: uuid.UUID, user_id: uuid.UUID, update_data: dict) -> Optional[Todo]:
        """
        Update an existing task
        
        Args:
            task_id: ID of the task
            user_id: ID of the user (for authorization)
            update_data: Fields to update
            
        Returns:
            Updated Todo item or None
        """
        task = self.session.get(Todo, task_id)
        if not task or task.user_id != user_id:
            return None
        
        for field, value in update_data.items():
            if value is not None:
                setattr(task, field, value)
        
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task
    
    def delete_task(self, task_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Delete a task
        
        Args:
            task_id: ID of the task
            user_id: ID of the user (for authorization)
            
        Returns:
            True if deleted, False if not found
        """
        task = self.session.get(Todo, task_id)
        if not task or task.user_id != user_id:
            return False
        
        self.session.delete(task)
        self.session.commit()
        return True
    
    def toggle_task_completion(self, task_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Todo]:
        """
        Toggle task completion status
        
        Args:
            task_id: ID of the task
            user_id: ID of the user (for authorization)
            
        Returns:
            Updated Todo item or None
        """
        task = self.session.get(Todo, task_id)
        if not task or task.user_id != user_id:
            return None
        
        task.is_completed = not task.is_completed
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task
    
    def get_tasks_by_priority(self, user_id: uuid.UUID, priority: str) -> List[Todo]:
        """
        Get tasks filtered by priority
        
        Args:
            user_id: ID of the user
            priority: Priority level to filter by
            
        Returns:
            List of Todo items with specified priority
        """
        statement = select(Todo).where(
            Todo.user_id == user_id,
            Todo.priority == priority
        )
        return self.session.exec(statement).all()
    
    def sort_tasks_by_priority(self, tasks: List[Todo], reverse: bool = False) -> List[Todo]:
        """
        Sort a list of tasks by priority
        
        Args:
            tasks: List of Todo items
            reverse: If True, sort low to high; if False, sort high to low
            
        Returns:
            Sorted list of Todo items
        """
        priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
        return sorted(tasks, key=lambda t: priority_order.get(t.priority, 4), reverse=not reverse)

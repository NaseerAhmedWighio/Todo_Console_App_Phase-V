from sqlmodel import SQLModel, Field, Column, DateTime, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone
import uuid

if TYPE_CHECKING:
    from .tag import TaskTag
    from .reminder import Reminder
    from .recurring_task import RecurringTask


def get_utc_now() -> datetime:
    """Get current UTC time - helper to avoid datetime.utcnow() deprecation"""
    return datetime.now(timezone.utc)


class TodoBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_completed: bool = Field(default=False)
    priority: str = Field(default="medium", max_length=20)  # low, medium, high, urgent
    due_date: Optional[datetime] = Field(default=None)


class Todo(TodoBase, table=True):
    __tablename__ = "todos"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=get_utc_now, sa_column=Column(DateTime(timezone=True)))
    updated_at: datetime = Field(default_factory=get_utc_now, sa_column=Column(DateTime(timezone=True)))

    # Advanced features fields
    timezone: Optional[str] = Field(default="UTC", max_length=50)
    is_recurring: bool = Field(default=False, index=True)
    recurring_task_id: Optional[uuid.UUID] = Field(default=None, foreign_key="recurring_tasks.id", index=True)
    
    # Additional fields that may exist in database
    recurrence_pattern: Optional[str] = Field(default="{}", max_length=500)
    reminder_settings: Optional[str] = Field(default="{}", max_length=1000)
    completed_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="todos")  # type: ignore
    task_tags: Optional[list["TaskTag"]] = Relationship(back_populates="task", sa_relationship_kwargs={"cascade": "all, delete-orphan"})  # type: ignore
    reminders: Optional[list["Reminder"]] = Relationship(back_populates="task", sa_relationship_kwargs={"cascade": "all, delete-orphan"})  # type: ignore
    recurring_task: Optional["RecurringTask"] = Relationship(
        back_populates="task",
        sa_relationship_kwargs={
            "primaryjoin": "RecurringTask.task_id == Todo.id"
        }
    )  # type: ignore


class TodoCreate(TodoBase):
    pass


class TodoUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None


class TodoResponse(TodoBase):
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
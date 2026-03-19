import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .todo import Todo


class RecurringTaskBase(SQLModel):
    recurrence_pattern: str = Field(max_length=50)  # daily, weekly, monthly, yearly, custom
    interval: int = Field(default=1, ge=1)
    by_weekday: Optional[str] = Field(default=None, max_length=50)  # Comma-separated 0-6 (0=Monday)
    by_monthday: Optional[int] = Field(default=None, ge=1, le=31)
    by_month: Optional[str] = Field(default=None, max_length=50)  # Comma-separated 1-12
    end_condition: str = Field(default="never", max_length=20)  # never, after_occurrences, on_date
    end_occurrences: Optional[int] = Field(default=None, ge=1)
    end_date: Optional[datetime] = Field(default=None)


class RecurringTask(RecurringTaskBase, table=True):
    __tablename__ = "recurring_tasks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    series_id: Optional[uuid.UUID] = Field(default=None, index=True)
    task_id: uuid.UUID = Field(foreign_key="todos.id", ondelete="CASCADE", index=True)
    last_generated_date: Optional[datetime] = Field(default=None)
    next_due_date: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    task: Optional["Todo"] = Relationship(
        back_populates="recurring_task", sa_relationship_kwargs={"primaryjoin": "RecurringTask.task_id == Todo.id"}
    )  # type: ignore


class RecurringTaskCreate(RecurringTaskBase):
    task_id: uuid.UUID


class RecurringTaskUpdate(SQLModel):
    recurrence_pattern: Optional[str] = None
    interval: Optional[int] = None
    by_weekday: Optional[str] = None
    by_monthday: Optional[int] = None
    by_month: Optional[str] = None
    end_condition: Optional[str] = None
    end_occurrences: Optional[int] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class RecurringTaskResponse(RecurringTaskBase):
    id: uuid.UUID
    task_id: uuid.UUID
    series_id: Optional[uuid.UUID]
    last_generated_date: Optional[datetime]
    next_due_date: Optional[datetime]
    is_active: bool
    created_at: datetime
    task_title: Optional[str] = None  # Computed field for API response

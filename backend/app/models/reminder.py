import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .todo import Todo
    from .user import User


class ReminderBase(SQLModel):
    timing_minutes: int = Field(default=0, ge=0)
    timing_days: Optional[int] = Field(default=None, ge=0)
    delivery_channel: str = Field(default="in_app", max_length=20)  # in_app, email, web_push, sms
    scheduled_time: datetime


class Reminder(ReminderBase, table=True):
    __tablename__ = "reminders"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id", ondelete="CASCADE", index=True)
    task_id: uuid.UUID = Field(foreign_key="todos.id", ondelete="CASCADE", index=True)
    reminder_type: Optional[str] = Field(default="scheduled", max_length=20)  # scheduled, email, push
    sent_at: Optional[datetime] = Field(default=None)
    status: str = Field(default="pending", max_length=20)  # pending, sent, failed, cancelled
    message: Optional[str] = Field(default=None)
    error_message: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    task: Optional["Todo"] = Relationship(back_populates="reminders")  # type: ignore
    user: Optional["User"] = Relationship(back_populates="reminders")  # type: ignore


class ReminderCreate(ReminderBase):
    task_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    reminder_type: Optional[str] = None


class ReminderUpdate(SQLModel):
    timing_minutes: Optional[int] = None
    timing_days: Optional[int] = None
    delivery_channel: Optional[str] = None
    reminder_type: Optional[str] = None


class ReminderResponse(ReminderBase):
    id: uuid.UUID
    task_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    reminder_type: Optional[str] = None
    sent_at: Optional[datetime]
    status: str
    message: Optional[str] = None
    created_at: datetime
    task_title: Optional[str] = None  # Computed field for API response

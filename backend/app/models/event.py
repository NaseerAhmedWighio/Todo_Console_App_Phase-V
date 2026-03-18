from sqlmodel import SQLModel, Field
from typing import Optional, Any
from datetime import datetime
import uuid
from sqlalchemy import Column, JSON, JSON as JsonType
from sqlalchemy.orm import Mapped, mapped_column


class DomainEventBase(SQLModel):
    event_type: str = Field(max_length=50)  # task.created, task.updated, task.completed, task.deleted, etc.
    aggregate_id: uuid.UUID
    aggregate_type: str = Field(max_length=50)  # Task, RecurringTask, Reminder, etc.
    user_id: uuid.UUID
    payload: Any = Field(sa_column=Column(JSON))
    event_metadata: Optional[Any] = Field(default=None, sa_column=Column("metadata", JSON))


class DomainEvent(DomainEventBase, table=True):
    __tablename__ = "domain_events"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    published: bool = Field(default=False, index=True)
    published_at: Optional[datetime] = Field(default=None)
    processed: bool = Field(default=False, index=True)
    processed_at: Optional[datetime] = Field(default=None)
    error_message: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class DomainEventCreate(DomainEventBase):
    pass


class DomainEventResponse(DomainEventBase):
    id: uuid.UUID
    published: bool
    published_at: Optional[datetime]
    processed: bool
    processed_at: Optional[datetime]
    created_at: datetime

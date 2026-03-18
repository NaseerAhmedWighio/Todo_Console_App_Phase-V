from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from .todo import Todo
    from .tag import Tag


class TaskTag(SQLModel, table=True):
    __tablename__ = "task_tags"

    task_id: uuid.UUID = Field(foreign_key="todos.id", ondelete="CASCADE", primary_key=True, index=True)
    tag_id: uuid.UUID = Field(foreign_key="tags.id", ondelete="CASCADE", primary_key=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    task: Optional["Todo"] = Relationship(back_populates="task_tags")  # type: ignore
    tag: Optional["Tag"] = Relationship(back_populates="task_tags")  # type: ignore

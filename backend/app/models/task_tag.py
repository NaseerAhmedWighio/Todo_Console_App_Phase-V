import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .tag import Tag
    from .todo import Todo


class TaskTag(SQLModel, table=True):
    __tablename__ = "task_tags"

    task_id: uuid.UUID = Field(foreign_key="todos.id", ondelete="CASCADE", primary_key=True, index=True)
    tag_id: uuid.UUID = Field(foreign_key="tags.id", ondelete="CASCADE", primary_key=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    task: Optional["Todo"] = Relationship(back_populates="task_tags")  # type: ignore
    tag: Optional["Tag"] = Relationship(back_populates="task_tags")  # type: ignore

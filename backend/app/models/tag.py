from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from .todo import TaskTag
    from .user import User


class TagBase(SQLModel):
    name: str = Field(min_length=1, max_length=50)
    color: str = Field(default="#6B7280", max_length=20)  # Hex color code


class Tag(TagBase, table=True):
    __tablename__ = "tags"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="tags")  # type: ignore
    task_tags: Optional[list["TaskTag"]] = Relationship(back_populates="tag", sa_relationship_kwargs={"cascade": "all, delete-orphan"})  # type: ignore


class TagCreate(TagBase):
    pass


class TagUpdate(SQLModel):
    name: Optional[str] = None
    color: Optional[str] = None


class TagResponse(TagBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    usage_count: Optional[int] = None  # Computed field for API response
    
    class Config:
        from_attributes = True

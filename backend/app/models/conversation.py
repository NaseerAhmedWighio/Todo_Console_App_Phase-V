import uuid
from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class Conversation(SQLModel, table=True):
    """
    Conversation model to store chat conversation data.
    """

    __tablename__ = "conversations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    title: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to user
    user: "User" = Relationship(back_populates="conversations")

    # Relationship to messages
    messages: List["Message"] = Relationship(back_populates="conversation", cascade_delete=True)

    def __init__(self, **data):
        super().__init__(**data)
        # Ensure updated_at is set to current time on initialization
        if not self.updated_at or self.updated_at == self.created_at:
            self.updated_at = datetime.utcnow()

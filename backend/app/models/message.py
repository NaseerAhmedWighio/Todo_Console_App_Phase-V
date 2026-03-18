from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
import uuid


class Message(SQLModel, table=True):
    """
    Message model to store individual chat messages.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversations.id", nullable=False)
    role: str = Field(nullable=False, max_length=20)  # 'user', 'assistant', or 'system'
    content: str = Field(nullable=False, max_length=10000)  # Up to 10k characters
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to conversation
    conversation: "Conversation" = Relationship(back_populates="messages")

    @property
    def is_valid_role(self) -> bool:
        """Check if the role is one of the allowed values."""
        return self.role in ['user', 'assistant', 'system']

    def __init__(self, **data):
        super().__init__(**data)
        # Validate role
        if hasattr(self, 'role') and not self.is_valid_role:
            raise ValueError(f"Role must be one of 'user', 'assistant', or 'system', got '{self.role}'")
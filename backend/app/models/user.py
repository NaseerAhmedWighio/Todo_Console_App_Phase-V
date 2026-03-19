import re
import uuid
from datetime import datetime, timezone
from typing import Optional

import bcrypt
from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel


def get_utc_now() -> datetime:
    """Get current UTC time - helper to avoid datetime.utcnow() deprecation"""
    return datetime.now(timezone.utc)


def is_google_email(email: str) -> bool:
    """
    Validate if an email is from Google.
    Checks for:
    - @gmail.com domain
    - @googlemail.com domain
    - Google Workspace domains (optional, can be configured)
    """
    if not email:
        return False

    email_lower = email.lower().strip()

    # Check for standard Google email domains
    google_domains = [
        "@gmail.com",
        "@googlemail.com",
    ]

    for domain in google_domains:
        if email_lower.endswith(domain):
            return True

    # Optional: Check for Google Workspace domains
    # You can add your organization's Google Workspace domain here
    # Example: if email_lower.endswith('@yourcompany.com'):
    #     return True

    return False


def validate_email_format(email: str) -> bool:
    """Validate email format using regex"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


class UserBase(SQLModel):
    email: str = Field(unique=True, index=True, min_length=5, max_length=255)
    name: Optional[str] = Field(default=None, max_length=255)


class User(UserBase, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    password_hash: str = Field(max_length=255, nullable=False)
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)

    # Advanced features fields
    timezone: str = Field(default="UTC", max_length=50)
    notification_preferences: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    default_task_priority: str = Field(default="medium", max_length=20)

    # Email verification
    is_email_verified: bool = Field(default=False)
    email_verified_at: Optional[datetime] = Field(default=None)

    # Relationship to Todos
    todos: Optional[list["Todo"]] = Relationship(back_populates="user")

    # Relationship to Conversations
    conversations: Optional[list["Conversation"]] = Relationship(back_populates="user", cascade_delete=True)

    # Relationship to Tags
    tags: Optional[list["Tag"]] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})  # type: ignore

    # Relationship to Reminders
    reminders: Optional[list["Reminder"]] = Relationship(back_populates="user")  # type: ignore


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)
    # Optional field to enforce Google email validation
    # If true, email must be from a Google domain (gmail.com, googlemail.com)
    google_email_only: Optional[bool] = Field(default=False)


class UserUpdate(SQLModel):
    name: Optional[str] = None


class UserLogin(SQLModel):
    email: str
    password: str


class UserResponse(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    is_email_verified: bool
    email_verified_at: Optional[datetime] = None


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

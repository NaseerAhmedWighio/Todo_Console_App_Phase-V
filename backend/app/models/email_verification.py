import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def get_utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(timezone.utc)


def get_expiration_time() -> datetime:
    """Get expiration time (24 hours from now)"""
    return get_utc_now() + timedelta(hours=24)


class EmailVerification(SQLModel, table=True):
    __tablename__ = "email_verifications"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(index=True, max_length=255, nullable=False)
    token: str = Field(unique=True, index=True, max_length=255, nullable=False)
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=get_utc_now)
    expires_at: datetime = Field(default_factory=get_expiration_time)
    verified_at: Optional[datetime] = Field(default=None)

    def is_token_expired(self) -> bool:
        """Check if the token has expired"""
        return get_utc_now() > self.expires_at

    @staticmethod
    def generate_token() -> str:
        """Generate a secure random token"""
        return secrets.token_urlsafe(32)

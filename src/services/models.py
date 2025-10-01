"""Data models for the authentication service."""

import datetime
import uuid
from dataclasses import dataclass, field


def utc_now() -> datetime.datetime:
    """Get current UTC datetime with timezone info."""
    return datetime.datetime.now(datetime.timezone.utc)


@dataclass
class User:
    """Represents a user in the authentication system."""

    email: str
    password_hash: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    is_active: bool = False
    created_at: datetime.datetime = field(default_factory=utc_now)


@dataclass
class ActivationCode:
    """Represents an activation code for user account activation."""

    user_id: str
    code: str
    created_at: datetime.datetime = field(default_factory=utc_now)
    expires_at: datetime.datetime | None = field(default=None)

    def __post_init__(self) -> None:
        if self.expires_at is None:
            # Code expires after 1 minute (client specification)
            self.expires_at = self.created_at + datetime.timedelta(minutes=1)

    @property
    def is_expired(self) -> bool:
        """Check if the activation code has expired."""
        if self.expires_at is None:
            return False

        now = utc_now()
        expires_at = self.expires_at

        # Handle timezone-naive expires_at by assuming UTC
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=datetime.timezone.utc)

        return now > expires_at

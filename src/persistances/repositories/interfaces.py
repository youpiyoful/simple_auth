"""Repository interfaces - pure abstractions without implementation details."""

from abc import ABC, abstractmethod

from src.services.models import ActivationCode, User


class UserRepositoryInterface(ABC):
    """Abstract interface for user repository operations."""

    @abstractmethod
    def create(self, user: User) -> User:
        """Create a new user."""

    @abstractmethod
    def get_by_id(self, user_id: str) -> User | None:
        """Get user by ID."""

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        """Get user by email."""

    @abstractmethod
    def update(self, user: User) -> User:
        """Update an existing user."""

    @abstractmethod
    def delete(self, user_id: str) -> bool:
        """Delete a user by ID."""

    @abstractmethod
    def list_all(self, limit: int = 100, offset: int = 0) -> list[User]:
        """List all users with pagination."""

    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""

    @abstractmethod
    def activate_user(self, user_id: str) -> bool:
        """Activate a user account."""


class ActivationCodeRepositoryInterface(ABC):
    """Abstract interface for activation code repository operations."""

    @abstractmethod
    def create(self, user_id: str) -> ActivationCode:
        """Create a new activation code for a user."""

    @abstractmethod
    def get_by_user_id(self, user_id: str) -> ActivationCode | None:
        """Get the latest activation code for a user."""

    @abstractmethod
    def get_by_code(self, code: str) -> ActivationCode | None:
        """Get activation code by code value."""

    @abstractmethod
    def delete(self, user_id: str) -> bool:
        """Delete activation code for a user."""

    @abstractmethod
    def cleanup_expired(self) -> int:
        """Remove expired activation codes. Returns number of codes removed."""

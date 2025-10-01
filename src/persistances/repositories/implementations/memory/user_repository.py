"""In-memory implementation of UserRepository for testing/demo purposes."""

from src.persistances.repositories.interfaces import UserRepositoryInterface
from src.services.models import User


class InMemoryUserRepository(UserRepositoryInterface):
    """In-memory implementation of UserRepository for demonstration/testing."""

    def __init__(self) -> None:
        self._users: dict[str, User] = {}  # user_id -> User
        self._email_index: dict[str, str] = {}  # email -> user_id

    def create(self, user: User) -> User:
        """Create a new user."""
        if user.id in self._users:
            raise ValueError(f"User with ID {user.id} already exists")

        if user.email in self._email_index:
            raise ValueError(f"User with email {user.email} already exists")

        self._users[user.id] = user
        self._email_index[user.email] = user.id
        return user

    def get_by_id(self, user_id: str) -> User | None:
        """Get user by ID."""
        return self._users.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        user_id: str | None = self._email_index.get(email)
        return self._users.get(user_id) if user_id else None

    def update(self, user: User) -> User:
        """Update an existing user."""
        if user.id not in self._users:
            raise ValueError(f"User with ID {user.id} not found")

        # Update email index if email changed
        old_user: User = self._users[user.id]
        if old_user.email != user.email:
            del self._email_index[old_user.email]
            self._email_index[user.email] = user.id

        self._users[user.id] = user
        return user

    def delete(self, user_id: str) -> bool:
        """Delete a user by ID."""
        if user_id in self._users:
            user: User = self._users[user_id]
            del self._email_index[user.email]
            del self._users[user_id]
            return True
        return False

    def list_all(self, limit: int = 100, offset: int = 0) -> list[User]:
        """List all users with pagination."""
        users: list[User] = list(self._users.values())
        return users[offset : offset + limit]

    def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        return email in self._email_index

    def activate_user(self, user_id: str) -> bool:
        """Activate a user account."""
        user: User | None = self.get_by_id(user_id=user_id)
        if not user:
            return False

        user.is_active = True
        self.update(user=user)
        return True

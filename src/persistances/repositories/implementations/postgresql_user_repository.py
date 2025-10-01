"""Simple PostgreSQL User Repository - just what we need."""

import logging

from src.persistances.db import get_db_cursor
from src.persistances.repositories.interfaces import UserRepositoryInterface
from src.services.models import User

logger = logging.getLogger(__name__)


class PostgreSQLUserRepository(UserRepositoryInterface):
    """Simple PostgreSQL implementation."""

    def create(self, user: User) -> User:
        """Create a new user."""
        query = """
            INSERT INTO users (id, email, password_hash, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
        """

        with get_db_cursor() as cursor:
            cursor.execute(
                query, (user.id, user.email, user.password_hash, user.is_active, user.created_at)
            )
            row = cursor.fetchone()

            return User(
                id=row["id"],
                email=row["email"],
                password_hash=row["password_hash"],
                is_active=row["is_active"],
                created_at=row["created_at"],
            )

    def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        query = "SELECT * FROM users WHERE email = %s"

        with get_db_cursor() as cursor:
            cursor.execute(query, (email,))
            row = cursor.fetchone()

            if row:
                return User(
                    id=row["id"],
                    email=row["email"],
                    password_hash=row["password_hash"],
                    is_active=row["is_active"],
                    created_at=row["created_at"],
                )
            return None

    def get_by_id(self, user_id: str) -> User | None:
        """Get user by ID."""
        query = "SELECT * FROM users WHERE id = %s"

        with get_db_cursor() as cursor:
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()

            if row:
                return User(
                    id=row["id"],
                    email=row["email"],
                    password_hash=row["password_hash"],
                    is_active=row["is_active"],
                    created_at=row["created_at"],
                )
            return None

    def update(self, user: User) -> User:
        """Update user."""
        query = """
            UPDATE users
            SET email = %s, password_hash = %s, is_active = %s
            WHERE id = %s
            RETURNING *
        """

        with get_db_cursor() as cursor:
            cursor.execute(query, (user.email, user.password_hash, user.is_active, user.id))
            row = cursor.fetchone()

            if not row:
                raise ValueError(f"User {user.id} not found")

            return User(
                id=row["id"],
                email=row["email"],
                password_hash=row["password_hash"],
                is_active=row["is_active"],
                created_at=row["created_at"],
            )

    def delete(self, user_id: str) -> bool:
        """Delete user."""
        query = "DELETE FROM users WHERE id = %s"

        with get_db_cursor() as cursor:
            cursor.execute(query, (user_id,))
            return cursor.rowcount > 0

    def list_all(self, limit: int = 100, offset: int = 0) -> list[User]:
        """List users."""
        query = "SELECT * FROM users LIMIT %s OFFSET %s"

        with get_db_cursor() as cursor:
            cursor.execute(query, (limit, offset))
            rows = cursor.fetchall()

            return [
                User(
                    id=row["id"],
                    email=row["email"],
                    password_hash=row["password_hash"],
                    is_active=row["is_active"],
                    created_at=row["created_at"],
                )
                for row in rows
            ]

    def exists_by_email(self, email: str) -> bool:
        """Check if user exists."""
        query = "SELECT 1 FROM users WHERE email = %s"

        with get_db_cursor() as cursor:
            cursor.execute(query, (email,))
            return cursor.fetchone() is not None

    def activate_user(self, user_id: str) -> bool:
        """Activate user."""
        query = "UPDATE users SET is_active = true WHERE id = %s"

        with get_db_cursor() as cursor:
            cursor.execute(query, (user_id,))
            return cursor.rowcount > 0

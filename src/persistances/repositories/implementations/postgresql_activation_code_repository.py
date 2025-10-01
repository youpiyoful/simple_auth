"""PostgreSQL implementation of activation code repository."""

import logging
import random
import string

from src.persistances.db import get_db_cursor
from src.persistances.repositories.interfaces import ActivationCodeRepositoryInterface
from src.services.models import ActivationCode

logger = logging.getLogger(__name__)


class PostgreSQLActivationCodeRepository(ActivationCodeRepositoryInterface):
    """PostgreSQL implementation of ActivationCodeRepository."""

    def create(self, user_id: str) -> ActivationCode:
        """Create a new 4-digit activation code for a user."""
        # Delete existing code first
        self.delete(user_id)

        # Generate unique 4-digit code
        code = self._generate_unique_code()

        query = """
            INSERT INTO activation_codes (user_id, code, created_at, expires_at)
            VALUES (%s, %s, NOW(), NOW() + INTERVAL '1 minute')
            RETURNING *
        """

        with get_db_cursor() as cursor:
            cursor.execute(query, (user_id, code))
            row = cursor.fetchone()

            return ActivationCode(
                user_id=row["user_id"],
                code=row["code"],
                created_at=row["created_at"],
                expires_at=row["expires_at"],
            )

    def get_by_user_id(self, user_id: str) -> ActivationCode | None:
        """Get the latest activation code for a user."""
        query = """
            SELECT * FROM activation_codes
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 1
        """

        with get_db_cursor() as cursor:
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()

            if row:
                return ActivationCode(
                    user_id=row["user_id"],
                    code=row["code"],
                    created_at=row["created_at"],
                    expires_at=row["expires_at"],
                )
            return None

    def get_by_code(self, code: str) -> ActivationCode | None:
        """Get activation code by code value."""
        query = "SELECT * FROM activation_codes WHERE code = %s"

        with get_db_cursor() as cursor:
            cursor.execute(query, (code,))
            row = cursor.fetchone()

            if row:
                return ActivationCode(
                    user_id=row["user_id"],
                    code=row["code"],
                    created_at=row["created_at"],
                    expires_at=row["expires_at"],
                )
            return None

    def delete(self, user_id: str) -> bool:
        """Delete activation codes for a user."""
        query = "DELETE FROM activation_codes WHERE user_id = %s"

        with get_db_cursor() as cursor:
            cursor.execute(query, (user_id,))
            return cursor.rowcount > 0

    def cleanup_expired(self) -> int:
        """Remove expired activation codes."""
        query = "DELETE FROM activation_codes WHERE expires_at < NOW()"

        with get_db_cursor() as cursor:
            cursor.execute(query)
            return cursor.rowcount

    def _generate_unique_code(self) -> str:
        """Generate a unique 4-digit code."""
        max_attempts = 10

        for _ in range(max_attempts):
            code = "".join(random.choices(string.digits, k=4))

            # Check if code already exists
            query = "SELECT 1 FROM activation_codes WHERE code = %s"
            with get_db_cursor() as cursor:
                cursor.execute(query, (code,))
                if not cursor.fetchone():
                    return code

        # If we can't find unique code after max_attempts, raise error
        raise ValueError("Could not generate unique activation code")

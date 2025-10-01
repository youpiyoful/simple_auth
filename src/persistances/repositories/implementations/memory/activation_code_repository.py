"""In-memory implementation of ActivationCodeRepository for testing/demo purposes."""

import random
import string

from src.persistances.repositories.interfaces import ActivationCodeRepositoryInterface
from src.services.models import ActivationCode


class InMemoryActivationCodeRepository(ActivationCodeRepositoryInterface):
    """In-memory implementation of ActivationCodeRepository for testing/demo."""

    def __init__(self) -> None:
        self._codes: dict[str, ActivationCode] = {}  # user_id -> ActivationCode
        self._code_index: dict[str, str] = {}  # code -> user_id

    def create(self, user_id: str) -> ActivationCode:
        """Create a new 4-digit activation code for a user."""
        # Supprimer l'ancien code si il existe
        self.delete(user_id=user_id)

        # Générer un code à 4 chiffres
        code: str = "".join(random.choices(population=string.digits, k=4))

        # S'assurer que le code est unique
        while code in self._code_index:
            code = "".join(random.choices(population=string.digits, k=4))

        activation_code = ActivationCode(user_id=user_id, code=code)

        self._codes[user_id] = activation_code
        self._code_index[code] = user_id

        return activation_code

    def get_by_user_id(self, user_id: str) -> ActivationCode | None:
        """Get the latest activation code for a user."""
        return self._codes.get(user_id)

    def get_by_code(self, code: str) -> ActivationCode | None:
        """Get activation code by code value."""
        user_id: str | None = self._code_index.get(code)
        if user_id:
            return self._codes.get(user_id)
        return None

    def delete(self, user_id: str) -> bool:
        """Delete activation code for a user."""
        if user_id in self._codes:
            activation_code: ActivationCode = self._codes[user_id]
            del self._code_index[activation_code.code]
            del self._codes[user_id]
            return True
        return False

    def cleanup_expired(self) -> int:
        """Remove expired activation codes."""
        expired_users: list[str] = []

        for user_id, activation_code in self._codes.items():
            if activation_code.is_expired:
                expired_users.append(user_id)

        for user_id in expired_users:
            self.delete(user_id=user_id)

        return len(expired_users)

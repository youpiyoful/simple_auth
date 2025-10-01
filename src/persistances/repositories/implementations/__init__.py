"""Repository implementations package."""

# PostgreSQL implementations (production)
# In-memory implementations (testing/demo)
from .memory import InMemoryActivationCodeRepository, InMemoryUserRepository
from .postgresql_activation_code_repository import PostgreSQLActivationCodeRepository
from .postgresql_user_repository import PostgreSQLUserRepository

__all__ = [
    # PostgreSQL (production)
    "PostgreSQLUserRepository",
    "PostgreSQLActivationCodeRepository",
    # In-memory (testing/demo)
    "InMemoryUserRepository",
    "InMemoryActivationCodeRepository",
]

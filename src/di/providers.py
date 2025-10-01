"""Providers for dependency injection."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

# Infrastructure imports
from src.persistances.email_client import MockMailer, SMTPMailer

# Repository implementations
from src.persistances.repositories.implementations import (
    PostgreSQLActivationCodeRepository,
    PostgreSQLUserRepository,
)

# Repository interfaces
from src.persistances.repositories.interfaces import (
    ActivationCodeRepositoryInterface,
    UserRepositoryInterface,
)

# Service imports
from src.services.user_service import UserService

T = TypeVar("T")


class Provider(ABC, Generic[T]):
    """Base provider interface."""

    @abstractmethod
    def provide(self) -> T:
        """Provide the dependency instance."""


class SingletonProvider(Provider[T]):
    """Provider that ensures singleton behavior."""

    def __init__(self, factory_func):
        self._factory = factory_func
        self._instance = None

    def provide(self) -> T:
        if self._instance is None:
            self._instance = self._factory()
        return self._instance


class RepositoryProvider:
    """Provider for repository layer dependencies."""

    def __init__(self, use_postgresql: bool = True):
        self._use_postgresql = use_postgresql
        self._user_repository = SingletonProvider(self._create_user_repository)
        self._activation_code_repository = SingletonProvider(
            self._create_activation_code_repository
        )

    def _create_user_repository(self) -> UserRepositoryInterface:
        """Factory for user repository."""
        if self._use_postgresql:
            return PostgreSQLUserRepository()
        else:
            from src.persistances.repositories.implementations.memory import InMemoryUserRepository

            return InMemoryUserRepository()

    def _create_activation_code_repository(self) -> ActivationCodeRepositoryInterface:
        """Factory for activation code repository."""
        if self._use_postgresql:
            return PostgreSQLActivationCodeRepository()
        else:
            from src.persistances.repositories.implementations.memory import (
                InMemoryActivationCodeRepository,
            )

            return InMemoryActivationCodeRepository()

    def get_user_repository(self) -> UserRepositoryInterface:
        """Get user repository instance."""
        return self._user_repository.provide()

    def get_activation_code_repository(self) -> ActivationCodeRepositoryInterface:
        """Get activation code repository instance."""
        return self._activation_code_repository.provide()


class InfrastructureProvider:
    """Provider for infrastructure layer dependencies."""

    def __init__(self, use_mock_email: bool = True):
        self._use_mock_email = use_mock_email
        self._email_client = SingletonProvider(self._create_email_client)

    def _create_email_client(self):
        """Factory for email client."""
        if self._use_mock_email:
            return MockMailer()
        else:
            # Configuration SMTP pour production
            return SMTPMailer(
                smtp_server="smtp.gmail.com",
                smtp_port=587,
                username="your-email@gmail.com",
                password="your-app-password",
            )

    def get_email_client(self):
        """Get email client instance."""
        return self._email_client.provide()


class ServiceProvider:
    """Provider for service layer dependencies."""

    def __init__(
        self,
        repository_provider: RepositoryProvider,
        infrastructure_provider: InfrastructureProvider,
    ):
        self._repository_provider = repository_provider
        self._infrastructure_provider = infrastructure_provider
        self._user_service = SingletonProvider(self._create_user_service)

    def _create_user_service(self) -> UserService:
        """Factory for user service."""
        return UserService(
            user_repo=self._repository_provider.get_user_repository(),
            activation_repo=self._repository_provider.get_activation_code_repository(),
            mailer=self._infrastructure_provider.get_email_client(),
        )

    def get_user_service(self) -> UserService:
        """Get user service instance."""
        return self._user_service.provide()

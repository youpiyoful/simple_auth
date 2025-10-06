"""Providers for dependency injection."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

# Infrastructure imports
from src.config.settings import AppSettings, SMTPSettings, get_settings
from src.persistances.email_client import EmailClientInterface, MockMailer, SMTPMailer

# Repository implementations
from src.persistances.repositories.implementations import (
    PostgreSQLActivationCodeRepository,
    PostgreSQLUserRepository,
)
from src.persistances.repositories.implementations.memory import InMemoryActivationCodeRepository
from src.persistances.repositories.implementations.memory.user_repository import (
    InMemoryUserRepository,
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

    def __init__(self, factory_func) -> None:
        self._factory = factory_func
        self._instance = None

    def provide(self) -> T:
        if self._instance is None:
            self._instance = self._factory()
        return self._instance


class RepositoryProvider:
    """Provider for repository layer dependencies."""

    def __init__(self, use_postgresql: bool = True) -> None:
        self._use_postgresql: bool = use_postgresql
        self._user_repository = SingletonProvider(self._create_user_repository)
        self._activation_code_repository = SingletonProvider(
            self._create_activation_code_repository
        )

    def _create_user_repository(self) -> UserRepositoryInterface:
        """Factory for user repository."""
        if self._use_postgresql:
            return PostgreSQLUserRepository()
        else:
            return InMemoryUserRepository()

    def _create_activation_code_repository(self) -> ActivationCodeRepositoryInterface:
        """Factory for activation code repository."""
        if self._use_postgresql:
            return PostgreSQLActivationCodeRepository()
        else:
            return InMemoryActivationCodeRepository()

    def get_user_repository(self) -> UserRepositoryInterface:
        """Get user repository instance."""
        return self._user_repository.provide()

    def get_activation_code_repository(self) -> ActivationCodeRepositoryInterface:
        """Get activation code repository instance."""
        return self._activation_code_repository.provide()


class InfrastructureProvider:
    """Provider for infrastructure layer dependencies."""

    def __init__(self, use_mock_email: bool = True) -> None:
        self._use_mock_email: bool = use_mock_email
        self._email_client = SingletonProvider(self._create_email_client)

    def _create_email_client(self) -> EmailClientInterface:
        """Factory for email client."""
        if self._use_mock_email:
            return MockMailer()
        else:
            # SMTP configuration via settings (allows using MailHog or real SMTP)
            settings: AppSettings = get_settings()
            smtp: SMTPSettings | None = settings.smtp_settings
            if smtp is None:
                raise ValueError(
                    "SMTP settings are not configured. Please provide smtp_settings in AppSettings or enable mock email (use_mock_email=True)."
                )
            return SMTPMailer(
                smtp_server=smtp.server,
                smtp_port=smtp.port,
                username=smtp.username,
                password=smtp.password,
                use_tls=smtp.use_tls,
            )

    def get_email_client(self) -> EmailClientInterface:
        """Get email client instance."""
        return self._email_client.provide()


class ServiceProvider:
    """Provider for service layer dependencies."""

    def __init__(
        self,
        repository_provider: RepositoryProvider,
        infrastructure_provider: InfrastructureProvider,
    ) -> None:
        self._repository_provider: RepositoryProvider = repository_provider
        self._infrastructure_provider: InfrastructureProvider = infrastructure_provider
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

"""Main dependency injection container."""

import os

from src.di.providers import InfrastructureProvider, RepositoryProvider, ServiceProvider
from src.persistances.repositories.interfaces import (
    ActivationCodeRepositoryInterface,
    UserRepositoryInterface,
)
from src.services.user_service import UserService


class AppContainer:
    """Main application container for dependency injection."""

    def __init__(self, use_mock_email: bool = True, use_postgresql: bool = True) -> None:
        """Initialize the container with configuration."""
        # Initialize providers in dependency order
        self._repository_provider = RepositoryProvider(use_postgresql=use_postgresql)
        self._infrastructure_provider = InfrastructureProvider(use_mock_email=use_mock_email)
        self._service_provider = ServiceProvider(
            repository_provider=self._repository_provider,
            infrastructure_provider=self._infrastructure_provider,
        )

    # Repository layer access
    def user_repository(self) -> UserRepositoryInterface:
        """Get user repository instance."""
        return self._repository_provider.get_user_repository()

    def activation_code_repository(self) -> ActivationCodeRepositoryInterface:
        """Get activation code repository instance."""
        return self._repository_provider.get_activation_code_repository()

    # Service layer access
    def user_service(self) -> UserService:
        """Get user service instance."""
        return self._service_provider.get_user_service()

    # Infrastructure layer access
    def email_client(self):  # -> Any:
        """Get email client instance."""
        return self._infrastructure_provider.get_email_client()

    # Utility methods
    def cleanup_resources(self) -> None:
        """Cleanup resources (connections, etc.)."""
        # Cleanup expired activation codes
        activation_repo: ActivationCodeRepositoryInterface = self.activation_code_repository()
        cleaned_count: int = activation_repo.cleanup_expired()
        if cleaned_count > 0:
            print(f"Cleaned up {cleaned_count} expired activation codes")

    def health_check(self) -> dict[str, str | dict[str, str]]:
        """Perform health check on all components."""
        health_status: dict[str, str | dict[str, str]] = {
            "container": "healthy",
            "repositories": {"user_repository": "healthy", "activation_code_repository": "healthy"},
            "services": {"user_service": "healthy"},
            "infrastructure": {"email_client": "healthy"},
        }

        try:
            # Test repository access
            self.user_repository()
            self.activation_code_repository()

            # Test service access
            self.user_service()

            # Test infrastructure access
            self.email_client()

        except (ImportError, AttributeError, ValueError) as e:
            health_status["container"] = f"unhealthy: {str(e)}"

        return health_status


class ContainerManager:
    """Manages the application container lifecycle without global state."""

    def __init__(self) -> None:
        self._container: AppContainer | None = None

    def get_container(self) -> AppContainer:
        """Get the application container instance (lazy initialization)."""
        if self._container is None:
            # Read configuration from environment
            use_mock_email: bool = os.getenv("USE_MOCK_EMAIL", "true").lower() == "true"
            self._container = AppContainer(use_mock_email=use_mock_email)
        return self._container

    def reset_container(self) -> None:
        """Reset the container (useful for testing)."""
        self._container = None

    def set_container(self, container: AppContainer) -> None:
        """Set a specific container (useful for testing)."""
        self._container = container


# Single instance of the container manager
_container_manager = ContainerManager()


def get_container() -> AppContainer:
    """Get the global application container instance."""
    return _container_manager.get_container()


def reset_container() -> None:
    """Reset the global container (useful for testing)."""
    _container_manager.reset_container()


def set_test_container(container: AppContainer) -> None:
    """Set a test container (useful for testing)."""
    _container_manager.set_container(container=container)


def create_test_container() -> AppContainer:
    """Create a container for testing with mocked dependencies."""
    return AppContainer(use_mock_email=True)

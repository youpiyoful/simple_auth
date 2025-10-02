"""FastAPI-specific dependencies and middleware."""

from typing import Annotated

from fastapi import Depends, Header, HTTPException

from src.di import get_container
from src.di.container import AppContainer
from src.services.exceptions import InvalidCredentials, UserNotFound
from src.services.models import User
from src.services.user_service import UserService


def get_user_service() -> UserService:
    """FastAPI dependency for UserService."""
    container: AppContainer = get_container()
    return container.user_service()


def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    user_service: UserService = Depends(dependency=get_user_service),
) -> User:
    """
    FastAPI dependency to get the current authenticated user.

    Extracts and validates Basic Auth credentials from the Authorization header.

    Args:
        authorization: Authorization header with Basic auth credentials
        user_service: Injected user service instance

    Returns:
        User: The authenticated and active user

    Raises:
        HTTPException: 401 if authentication fails or user not found
                      403 if account is not activated
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Basic"},
        )

    try:
        user: User = user_service.authenticate_basic(authorization_header=authorization)
        return user
    except (InvalidCredentials, UserNotFound) as e:
        # All authentication failures should return 401 with WWW-Authenticate header
        # to trigger browser's Basic Auth prompt
        raise HTTPException(
            status_code=401, detail="Invalid credentials", headers={"WWW-Authenticate": "Basic"}
        ) from e


def require_active_user(current_user: User = Depends(dependency=get_current_user)) -> User:
    """
    FastAPI dependency to ensure the user account is activated.

    Args:
        current_user: The authenticated user from get_current_user

    Returns:
        User: The authenticated and active user

    Raises:
        HTTPException: 403 if account is not activated
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Account not activated. Please check your email for activation code.",
        )
    return current_user


def get_container_health() -> dict[str, str | dict[str, str]]:
    """FastAPI dependency for container health check."""
    container: AppContainer = get_container()
    return container.health_check()

"""User-related API routes."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr

from src.api.deps import get_container_health, get_current_user, get_user_service
from src.services.exceptions import (  # InvalidCredentials,
    ActivationCodeExpired,
    InvalidActivationCode,
    UserNotFound,
)
from src.services.models import User
from src.services.user_service import UserService

router = APIRouter(tags=["auth"])


# Pydantic models for request/response
class RegisterRequest(BaseModel):
    """Request model for user registration."""

    email: EmailStr
    password: str


class ActivationRequest(BaseModel):
    """Request model for account activation."""

    activation_code: str


class ResendCodeRequest(BaseModel):
    """Request model for resending activation code."""

    email: EmailStr


class UserResponse(BaseModel):
    """Response model for user info."""

    id: str
    email: str
    is_active: bool


class MessageResponse(BaseModel):
    """Generic message response model."""

    message: str


class RegisterResponse(BaseModel):
    """Response model for user registration."""

    message: str
    user_id: str | None = None


# Dependency injection is handled in src/api/deps.py


@router.post("/register", response_model=RegisterResponse, status_code=201)
def register(
    request: RegisterRequest, user_service: UserService = Depends(dependency=get_user_service)
) -> RegisterResponse:
    """Register a new user and send activation email."""
    # Toujours retourner le même message pour éviter l'énumération d'emails
    user = user_service.register(email=request.email, password=request.password)

    # Si l'utilisateur est créé, retourner son ID pour les tests
    user_id = user.id if user is not None else None

    return RegisterResponse(
        message="User registered successfully. Check your email for activation code.",
        user_id=user_id,
    )


@router.post("/activate", response_model=MessageResponse)
def activate_account(
    request: ActivationRequest, user_service: UserService = Depends(dependency=get_user_service)
) -> MessageResponse:
    """Activate user account with 4-digit code."""
    try:
        user_service.activate_account(activation_code=request.activation_code)
        return MessageResponse(message="Account activated successfully.")
    except InvalidActivationCode as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except ActivationCodeExpired as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except UserNotFound as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/resend-code", response_model=MessageResponse)
def resend_activation_code(
    request: ResendCodeRequest, user_service: UserService = Depends(dependency=get_user_service)
) -> MessageResponse:
    """Resend activation code to user email."""
    try:
        success = user_service.resend_activation_code(email=request.email)
        if success:
            return MessageResponse(message="Activation code sent to your email.")
        else:
            return MessageResponse(message="Account already activated.")
    except UserNotFound as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/me", response_model=UserResponse)
def get_user_info(current_user: User = Depends(dependency=get_current_user)) -> UserResponse:
    """Get current user info using Basic Auth."""
    return UserResponse(
        id=current_user.id, email=current_user.email, is_active=current_user.is_active
    )


@router.get("/health")
def health_check() -> dict[str, str | dict[str, str | dict[str, str]]]:
    """Complete health check endpoint with container status."""
    container_health: dict[str, str | dict[str, str]] = get_container_health()
    return {
        "status": "healthy" if container_health["container"] == "healthy" else "unhealthy",
        "service": "simple_auth",
        "details": container_health,
    }

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

router = APIRouter(tags=["users"])


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


class ActivateUserRequest(BaseModel):
    """Request model for user activation."""

    activation_code: str


class ResendCodeByIdRequest(BaseModel):
    """Request model for resending activation code by user ID."""

    email: EmailStr


# Dependency injection is handled in src/api/deps.py


# POST /api/v1/users - Create a new user
@router.post("/api/v1/users", response_model=RegisterResponse, status_code=201)
def create_user(
    request: RegisterRequest, user_service: UserService = Depends(get_user_service)
) -> RegisterResponse:
    """Create a new user and send activation email."""
    user = user_service.register(email=request.email, password=request.password)
    user_id = user.id if user is not None else None

    return RegisterResponse(
        message="User registered successfully. Check your email for activation code.",
        user_id=user_id,
    )


# PATCH /api/v1/users/{id} - Activate a user
@router.patch("/api/v1/users/{user_id}", response_model=MessageResponse)
def activate_user(
    user_id: str,
    request: ActivateUserRequest,
    user_service: UserService = Depends(get_user_service),
) -> MessageResponse:
    """Activate user account with activation code."""
    try:
        # Note: user_id is in path but service uses code-based lookup
        user_service.activate_account(activation_code=request.activation_code)
        return MessageResponse(message="Account activated successfully.")
    except InvalidActivationCode as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except ActivationCodeExpired as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except UserNotFound as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


# POST /api/v1/users/{id}/codes - Generate or resend activation code
@router.post("/api/v1/users/{user_id}/codes", response_model=MessageResponse)
def generate_or_resend_code(
    user_id: str,
    request: ResendCodeByIdRequest,
    user_service: UserService = Depends(get_user_service),
) -> MessageResponse:
    """Generate or resend activation code to user email."""
    try:
        # RESTful: user_id in path, email in body for service compatibility
        success = user_service.resend_activation_code(email=request.email)
        if success:
            return MessageResponse(message="Activation code sent to your email.")
        else:
            return MessageResponse(message="Account already activated.")
    except UserNotFound as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


# GET /api/v1/users/me - Get current user profile
@router.get("/api/v1/users/me", response_model=UserResponse)
def get_user_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Get current user info using Basic Auth."""
    return UserResponse(
        id=current_user.id, email=current_user.email, is_active=current_user.is_active
    )


# GET /api/v1/health - Health check endpoint
@router.get("/api/v1/health")
def health_check() -> dict[str, str | dict[str, str | dict[str, str]]]:
    """Complete health check endpoint with container status."""
    container_health: dict[str, str | dict[str, str]] = get_container_health()
    return {
        "status": "healthy" if container_health["container"] == "healthy" else "unhealthy",
        "service": "simple_auth",
        "details": container_health,
    }

"""Custom error handlers for the FastAPI application."""

from fastapi import Request
from fastapi.responses import JSONResponse

from src.services.exceptions import (
    AccountNotActivated,
    ActivationCodeInvalid,
    InvalidCredentials,
    PasswordTooWeak,
    PermissionDenied,
    UserAlreadyExists,
    UserNotFound,
)


def add_error_handlers(app) -> None:
    """Attach custom exception handlers to the FastAPI app."""

    @app.exception_handler(UserAlreadyExists)
    def user_already_exists_handler(_request: Request, _exc: UserAlreadyExists) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": "User already exists"},
        )

    @app.exception_handler(UserNotFound)
    def user_not_found_handler(_request: Request, _exc: UserNotFound) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"detail": "User not found"},
        )

    @app.exception_handler(InvalidCredentials)
    def invalid_credentials_handler(_request: Request, _exc: InvalidCredentials) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid credentials"},
        )

    @app.exception_handler(ActivationCodeInvalid)
    def activation_code_invalid_handler(
        _request: Request, _exc: ActivationCodeInvalid
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid or expired activation code"},
        )

    @app.exception_handler(AccountNotActivated)
    def account_not_activated_handler(_request: Request, _exc: AccountNotActivated) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={"detail": "Account not activated"},
        )

    @app.exception_handler(PermissionDenied)
    def permission_denied_handler(_request: Request, _exc: PermissionDenied) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={"detail": "Permission denied"},
        )

    @app.exception_handler(PasswordTooWeak)
    def password_too_weak_handler(_request: Request, _exc: PasswordTooWeak) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": "Password too weak"},
        )

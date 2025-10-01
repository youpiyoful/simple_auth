"""Custom exceptions for the authentication service."""


class AuthenticationError(Exception):
    """Base class for all authentication-related exceptions."""


class UserAlreadyExists(AuthenticationError):
    """Raised when trying to register a user that already exists."""

    def __init__(self, email=None):
        self.email = email
        message = f"User with email {email} already exists" if email else "User already exists"
        super().__init__(message)


class UserNotFound(AuthenticationError):
    """Raised when a user lookup fails."""

    def __init__(self, username=None):
        self.username = username
        message = f"User '{username}' not found" if username else "User not found"
        super().__init__(message)


class InvalidCredentials(AuthenticationError):
    """Raised when login credentials are invalid."""

    def __init__(self, message="Invalid username or password"):
        super().__init__(message)


class ActivationCodeInvalid(AuthenticationError):
    """Raised when the provided activation code is invalid or expired."""

    def __init__(self, message="Activation code is invalid or expired"):
        super().__init__(message)


class InvalidActivationCode(AuthenticationError):
    """Raised when the activation code format is invalid."""

    def __init__(self, message="Invalid activation code"):
        super().__init__(message)


class ActivationCodeExpired(AuthenticationError):
    """Raised when the activation code has expired."""

    def __init__(self, message="Activation code has expired"):
        super().__init__(message)


class AccountNotActivated(AuthenticationError):
    """Raised when trying to login with an unactivated account."""

    def __init__(self, message="Account has not been activated"):
        super().__init__(message)


class PermissionDenied(AuthenticationError):
    """Raised when user lacks required permissions."""

    def __init__(self, message="Permission denied"):
        super().__init__(message)


class PasswordTooWeak(AuthenticationError):
    """Raised when password doesn't meet security requirements."""

    def __init__(self, message="Password does not meet security requirements"):
        super().__init__(message)

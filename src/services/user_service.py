"""User service for authentication and account management."""

import base64

import bcrypt

from src.persistances.repositories.interfaces import (
    ActivationCodeRepositoryInterface,
    UserRepositoryInterface,
)
from src.services.exceptions import (
    ActivationCodeExpired,
    InvalidActivationCode,
    InvalidCredentials,
    UserNotFound,
)
from src.services.models import ActivationCode, User


class UserService:
    """Service for user authentication and account management."""

    def __init__(
        self,
        user_repo: UserRepositoryInterface,
        activation_repo: ActivationCodeRepositoryInterface,
        mailer,
    ) -> None:
        self.user_repo = user_repo
        self.activation_repo = activation_repo
        self.mailer = mailer

    def register(self, email: str, password: str) -> User | None:
        """Register a new user and send activation email."""
        # Vérifier si l'utilisateur existe déjà (retourner None pour éviter l'énumération d'emails)
        if self.user_repo.exists_by_email(email=email):
            return None

        # Hasher le mot de passe
        password_hash: str = bcrypt.hashpw(
            password=password.encode(), salt=bcrypt.gensalt()
        ).decode()

        # Créer l'utilisateur (inactif par défaut)
        user = User(email=email, password_hash=password_hash, is_active=False)
        created_user: User = self.user_repo.create(user=user)

        # Générer et envoyer le code d'activation
        activation_code: ActivationCode = self.activation_repo.create(user_id=created_user.id)
        self.mailer.send_activation_email(email, activation_code.code)

        return created_user

    def activate_account(self, activation_code: str) -> bool:
        """Activate user account with activation code."""
        # Trouver le code d'activation
        code_obj: ActivationCode | None = self.activation_repo.get_by_code(activation_code)
        if not code_obj:
            raise InvalidActivationCode(message="Invalid activation code")

        # Vérifier si le code a expiré
        if code_obj.is_expired:
            self.activation_repo.delete(user_id=code_obj.user_id)
            raise ActivationCodeExpired(message="Activation code has expired")

        # Activer l'utilisateur
        success: bool = self.user_repo.activate_user(user_id=code_obj.user_id)
        if success:
            # Supprimer le code d'activation utilisé
            self.activation_repo.delete(user_id=code_obj.user_id)
            return True

        raise UserNotFound(username="User not found")

    def resend_activation_code(self, email: str) -> bool:
        """Resend activation code to user email."""
        user: User | None = self.user_repo.get_by_email(email=email)
        if not user:
            raise UserNotFound(username=f"User with email {email} not found")

        if user.is_active:
            return False  # Utilisateur déjà activé

        # Générer un nouveau code
        activation_code: ActivationCode = self.activation_repo.create(user_id=user.id)
        self.mailer.send_activation_email(email, activation_code.code)
        return True

    def authenticate(self, email: str, password: str) -> User:
        """Authenticate user with email and password (Basic Auth)."""
        user: User | None = self.user_repo.get_by_email(email=email)
        if not user:
            raise UserNotFound(username=f"User with email {email} not found")

        if not user.is_active:
            raise InvalidCredentials(message="Account not activated")

        # Vérifier le mot de passe
        if bcrypt.checkpw(password=password.encode(), hashed_password=user.password_hash.encode()):
            return user

        raise InvalidCredentials(message="Invalid credentials")

    def authenticate_basic(self, authorization_header: str) -> User:
        """Authenticate user from Basic Auth header."""
        if not authorization_header.startswith("Basic "):
            raise InvalidCredentials(message="Invalid authorization header")

        try:
            # Décoder le header Basic Auth
            encoded_credentials: str = authorization_header.split(" ")[1]
            decoded_credentials: str = base64.b64decode(encoded_credentials).decode(
                encoding="utf-8"
            )
            email, password = decoded_credentials.split(":", 1)

            return self.authenticate(email=email, password=password)
        except (ValueError, IndexError) as exc:
            raise InvalidCredentials(message="Invalid authorization header format") from exc

    def get_user_by_email(self, email: str) -> User | None:
        """Get user by email."""
        return self.user_repo.get_by_email(email=email)

    def cleanup_expired_codes(self) -> int:
        """Clean up expired activation codes."""
        return self.activation_repo.cleanup_expired()

"""Tests for Simple Auth API - Production Ready Test Suite."""

import time
from unittest.mock import Mock

import pytest

from src.persistances.repositories.activation_code_repository import ActivationCodeRepository
from src.persistances.repositories.user_repository import UserRepository
from src.services.exceptions import (
    ActivationCodeExpired,
    InvalidActivationCode,
    InvalidCredentials,
    UserNotFound,
)
from src.services.models import ActivationCode, User
from src.services.user_service import UserService


class TestUserService:
    """Test suite for UserService - Core Business Logic."""

    def setup_method(self):
        """Setup fresh instances for each test."""
        self.user_repo = UserRepository()
        self.activation_repo = ActivationCodeRepository()
        self.mock_mailer = Mock()
        self.user_service = UserService(
            user_repo=self.user_repo, activation_repo=self.activation_repo, mailer=self.mock_mailer
        )

    def test_register_new_user_success(self):
        """Test successful user registration."""
        # Given
        email = "test@example.com"
        password = "password123"

        # When
        user = self.user_service.register(email, password)

        # Then
        assert user is not None
        assert user.email == email
        assert not user.is_active  # Should be inactive initially
        assert user.id is not None

        # Verify email was sent
        self.mock_mailer.send_activation_email.assert_called_once()
        call_args = self.mock_mailer.send_activation_email.call_args
        assert call_args[0][0] == email  # First arg is email
        assert len(call_args[0][1]) == 4  # Second arg is 4-digit code
        assert call_args[0][1].isdigit()  # Code should be numeric

    def test_register_existing_user_returns_none(self):
        """Test registration with existing email returns None (security)."""
        # Given
        email = "test@example.com"
        password = "password123"

        # Register first user
        self.user_service.register(email, password)

        # When - try to register same email
        result = self.user_service.register(email, "different_password")

        # Then
        assert result is None  # Should return None for existing user

        # Verify no second email was sent
        assert self.mock_mailer.send_activation_email.call_count == 1

    def test_activate_account_success(self):
        """Test successful account activation."""
        # Given
        email = "test@example.com"
        password = "password123"

        # Register user
        user = self.user_service.register(email, password)
        assert user is not None

        # Get the activation code
        activation_code = self.activation_repo.get_by_user_id(user.id)
        assert activation_code is not None

        # When
        success = self.user_service.activate_account(activation_code.code)

        # Then
        assert success is True

        # Verify user is now active
        updated_user = self.user_repo.get_by_id(user.id)
        assert updated_user is not None
        assert updated_user.is_active is True

    def test_activate_account_invalid_code(self):
        """Test activation with invalid code."""
        # Given
        invalid_code = "9999"

        # When/Then
        with pytest.raises(InvalidActivationCode):
            self.user_service.activate_account(invalid_code)

    def test_activate_account_expired_code(self):
        """Test activation with expired code."""
        # Given
        email = "test@example.com"
        password = "password123"

        # Register user
        user = self.user_service.register(email, password)
        assert user is not None

        activation_code = self.activation_repo.get_by_user_id(user.id)
        assert activation_code is not None

        # Manually expire the code by setting expires_at to past
        import datetime

        activation_code.expires_at = datetime.datetime.now() - datetime.timedelta(seconds=1)

        # When/Then
        with pytest.raises(ActivationCodeExpired):
            self.user_service.activate_account(activation_code.code)

    def test_authenticate_success(self):
        """Test successful authentication."""
        # Given
        email = "test@example.com"
        password = "password123"

        # Register and activate user
        user = self.user_service.register(email, password)
        assert user is not None

        activation_code = self.activation_repo.get_by_user_id(user.id)
        assert activation_code is not None

        self.user_service.activate_account(activation_code.code)

        # When
        authenticated_user = self.user_service.authenticate(email, password)

        # Then
        assert authenticated_user is not None
        assert authenticated_user.email == email
        assert authenticated_user.is_active is True

    def test_authenticate_wrong_password(self):
        """Test authentication with wrong password."""
        # Given
        email = "test@example.com"
        password = "password123"

        # Register and activate user
        user = self.user_service.register(email, password)
        assert user is not None

        activation_code = self.activation_repo.get_by_user_id(user.id)
        assert activation_code is not None

        self.user_service.activate_account(activation_code.code)

        # When/Then
        with pytest.raises(InvalidCredentials):
            self.user_service.authenticate(email, "wrong_password")

    def test_authenticate_inactive_user(self):
        """Test authentication with inactive user."""
        # Given
        email = "test@example.com"
        password = "password123"

        # Register user but don't activate
        self.user_service.register(email, password)

        # When/Then
        with pytest.raises(InvalidCredentials):
            self.user_service.authenticate(email, password)

    def test_authenticate_nonexistent_user(self):
        """Test authentication with non-existent user."""
        # When/Then
        with pytest.raises(UserNotFound):
            self.user_service.authenticate("nonexistent@example.com", "password")

    def test_authenticate_basic_auth_header(self):
        """Test Basic Auth header parsing."""
        # Given
        email = "test@example.com"
        password = "password123"

        # Register and activate user
        user = self.user_service.register(email, password)
        assert user is not None

        activation_code = self.activation_repo.get_by_user_id(user.id)
        assert activation_code is not None

        self.user_service.activate_account(activation_code.code)

        # Create Basic Auth header
        import base64

        credentials = base64.b64encode(f"{email}:{password}".encode()).decode()
        auth_header = f"Basic {credentials}"

        # When
        authenticated_user = self.user_service.authenticate_basic(auth_header)

        # Then
        assert authenticated_user.email == email

    def test_resend_activation_code(self):
        """Test resending activation code."""
        # Given
        email = "test@example.com"
        password = "password123"

        # Register user
        self.user_service.register(email, password)

        # When
        success = self.user_service.resend_activation_code(email)

        # Then
        assert success is True
        assert self.mock_mailer.send_activation_email.call_count == 2  # Original + resend


class TestActivationCodeExpiry:
    """Test suite specifically for 1-minute expiration requirement."""

    def setup_method(self):
        """Setup test environment."""
        self.activation_repo = ActivationCodeRepository()

    def test_activation_code_expires_after_one_minute(self):
        """Test that activation codes expire after exactly 1 minute."""
        # Given
        user_id = "test-user-123"

        # When
        activation_code = self.activation_repo.create(user_id)
        assert activation_code is not None

        # Then
        import datetime

        expected_expiry = activation_code.created_at + datetime.timedelta(minutes=1)

        # Verify expires_at is set correctly
        assert activation_code.expires_at is not None

        # Allow small tolerance for test execution time
        time_diff = abs((activation_code.expires_at - expected_expiry).total_seconds())
        assert time_diff < 1  # Should be within 1 second

        # Verify it's considered not expired immediately
        assert not activation_code.is_expired

        # Manually set time to just over 1 minute and verify expiration
        activation_code.expires_at = datetime.datetime.now() - datetime.timedelta(seconds=1)
        assert activation_code.is_expired


if __name__ == "__main__":
    # Run tests with: python -m pytest tests/test_simple_auth.py -v
    pytest.main([__file__, "-v"])

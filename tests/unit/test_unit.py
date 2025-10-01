"""Unit tests for Simple Auth - Fast tests using in-memory implementations."""

import uuid

import pytest

from src.di.container import AppContainer
from src.services.exceptions import (
    ActivationCodeExpired,
    InvalidActivationCode,
    InvalidCredentials,
    UserNotFound,
)


@pytest.mark.unit
class TestUserServiceUnit:
    """Unit tests for UserService using in-memory repositories."""

    def setup_method(self):
        """Setup fresh in-memory container for each test."""
        # Use in-memory implementations for fast tests
        self.container = AppContainer(use_postgresql=False, use_mock_email=True)
        self.user_service = self.container.user_service()
        self.user_repo = self.container.user_repository()
        self.activation_repo = self.container.activation_code_repository()

    def test_user_registration_success(self):
        """Test successful user registration creates user and activation code."""
        # Given
        email = f"test-{uuid.uuid4().hex[:8]}@example.com"
        password = "password123"

        # When
        user = self.user_service.register(email, password)

        # Then
        assert user is not None
        assert user.email == email
        assert user.is_active is False
        assert user.password_hash != password  # Should be hashed

        # Activation code should be created
        activation_code = self.activation_repo.get_by_user_id(user.id)
        assert activation_code is not None
        assert len(activation_code.code) == 4
        assert activation_code.code.isdigit()

    def test_user_registration_duplicate_email(self):
        """Test that duplicate email registration returns None (security)."""
        # Given
        email = f"duplicate-{uuid.uuid4().hex[:8]}@example.com"
        password = "password123"

        # First registration
        user1 = self.user_service.register(email, password)
        assert user1 is not None

        # Second registration with same email
        user2 = self.user_service.register(email, password)
        assert user2 is None  # Should return None for security

    def test_activation_code_success(self):
        """Test successful account activation."""
        # Given - Register user
        email = f"activate-{uuid.uuid4().hex[:8]}@example.com"
        user = self.user_service.register(email, "password123")
        assert user is not None
        activation_code = self.activation_repo.get_by_user_id(user.id)
        assert activation_code is not None

        # When - Activate account
        self.user_service.activate_account(activation_code.code)

        # Then - User should be active and code should be deleted
        updated_user = self.user_repo.get_by_id(user.id)
        assert updated_user is not None
        assert updated_user.is_active is True

        remaining_code = self.activation_repo.get_by_user_id(user.id)
        assert remaining_code is None

    def test_activation_code_invalid(self):
        """Test activation with invalid code raises error."""
        # Given
        invalid_code = "9999"

        # When/Then
        try:
            self.user_service.activate_account(invalid_code)
            assert False, "Should have raised InvalidActivationCode"
        except InvalidActivationCode:
            pass

    def test_activation_code_expired(self):
        """Test activation with expired code raises error."""
        # Given - Register user and expire the code
        email = f"expired-{uuid.uuid4().hex[:8]}@example.com"
        user = self.user_service.register(email, "password123")
        assert user is not None
        activation_code = self.activation_repo.get_by_user_id(user.id)
        assert activation_code is not None

        # Manually expire the code (in-memory, we can modify directly)
        import datetime

        activation_code.expires_at = datetime.datetime.now(
            datetime.timezone.utc
        ) - datetime.timedelta(seconds=1)

        # When/Then
        try:
            self.user_service.activate_account(activation_code.code)
            assert False, "Should have raised ActivationCodeExpired"
        except ActivationCodeExpired:
            pass

    def test_authentication_success(self):
        """Test successful authentication with activated user."""
        # Given - Register and activate user
        email = f"auth-{uuid.uuid4().hex[:8]}@example.com"
        password = "password123"
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

    def test_authentication_invalid_credentials(self):
        """Test authentication with wrong password raises error."""
        # Given - Register and activate user
        email = f"badpass-{uuid.uuid4().hex[:8]}@example.com"
        user = self.user_service.register(email, "password123")
        assert user is not None
        activation_code = self.activation_repo.get_by_user_id(user.id)
        assert activation_code is not None
        self.user_service.activate_account(activation_code.code)

        # When/Then
        try:
            self.user_service.authenticate(email, "wrongpassword")
            assert False, "Should have raised InvalidCredentials"
        except InvalidCredentials:
            pass

    def test_authentication_user_not_found(self):
        """Test authentication with non-existent user raises error."""
        # Given
        fake_email = f"notfound-{uuid.uuid4().hex[:8]}@example.com"

        # When/Then
        try:
            self.user_service.authenticate(fake_email, "password123")
            assert False, "Should have raised UserNotFound"
        except UserNotFound:
            pass

    def test_authentication_inactive_user(self):
        """Test authentication with inactive user raises error."""
        # Given - Register but don't activate
        email = f"inactive-{uuid.uuid4().hex[:8]}@example.com"
        user = self.user_service.register(email, "password123")

        # When/Then
        try:
            self.user_service.authenticate(email, "password123")
            assert False, "Should have raised InvalidCredentials"
        except InvalidCredentials:
            pass


@pytest.mark.unit
class TestActivationCodeModelUnit:
    """Unit tests for ActivationCode model logic."""

    def test_activation_code_expiration_timing(self):
        """Test that activation codes expire after exactly 1 minute."""
        import datetime

        from src.services.models import ActivationCode

        # Given
        now = datetime.datetime.now(datetime.timezone.utc)
        code = ActivationCode(user_id="test-user", code="1234")

        # Then - should expire after 1 minute
        expected_expiry = now + datetime.timedelta(minutes=1)
        # Allow 1 second tolerance for test execution time
        assert code.expires_at is not None
        assert abs((code.expires_at - expected_expiry).total_seconds()) < 1

        # Should not be expired initially
        assert not code.is_expired

        # Should be expired if we set expires_at to past
        code.expires_at = now - datetime.timedelta(seconds=1)
        assert code.is_expired


@pytest.mark.unit
class TestRepositoryPatternsUnit:
    """Unit tests for repository implementations."""

    def setup_method(self):
        """Setup fresh in-memory repositories."""
        self.container = AppContainer(use_postgresql=False, use_mock_email=True)
        self.user_repo = self.container.user_repository()
        self.activation_repo = self.container.activation_code_repository()

    def test_user_repository_crud(self):
        """Test user repository basic CRUD operations."""
        from src.services.models import User

        # Create
        user = User(email="test@example.com", password_hash="hashed")
        created_user = self.user_repo.create(user)
        assert created_user.id is not None
        assert created_user.email == user.email

        # Read
        found_user = self.user_repo.get_by_email("test@example.com")
        assert found_user is not None
        assert found_user.id == created_user.id

        found_by_id = self.user_repo.get_by_id(created_user.id)
        assert found_by_id is not None
        assert found_by_id.email == "test@example.com"

        # Exists check
        assert self.user_repo.exists_by_email("test@example.com") is True
        assert self.user_repo.exists_by_email("notfound@example.com") is False

        # Update
        created_user.is_active = True
        updated_user = self.user_repo.update(created_user)
        assert updated_user.is_active is True

    def test_activation_code_repository_operations(self):
        """Test activation code repository operations."""
        # Create code
        code = self.activation_repo.create("user-123")
        assert code is not None
        assert len(code.code) == 4
        assert code.code.isdigit()
        assert code.user_id == "user-123"

        # Get by user ID
        found_code = self.activation_repo.get_by_user_id("user-123")
        assert found_code is not None
        assert found_code.code == code.code

        # Get by code value
        found_by_code = self.activation_repo.get_by_code(code.code)
        assert found_by_code is not None
        assert found_by_code.user_id == "user-123"

        # Delete
        deleted = self.activation_repo.delete("user-123")
        assert deleted is True

        # Should not find after delete
        assert self.activation_repo.get_by_user_id("user-123") is None
        assert self.activation_repo.get_by_code(code.code) is None

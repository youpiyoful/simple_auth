"""Integration tests for Simple Auth API endpoints.

These tests use real PostgreSQL database to test end-to-end functionality.
They are slower than unit tests but validate the complete system behavior.

Requirements:
- Docker must be running
- PostgreSQL container must be available (docker-compose up -d db)
"""

import base64
import json
import time
import uuid

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.mark.integration
class TestAPIIntegration:
    """Integration tests for the complete API workflow."""

    def setup_method(self):
        """Setup fresh client for each test."""
        self.client = TestClient(app)

    def test_complete_user_registration_flow(self):
        """Test the complete user registration and activation flow."""
        # Given
        unique_email = f"integration-{uuid.uuid4().hex[:8]}@example.com"
        user_data = {"email": unique_email, "password": "password123"}

        # Step 1: Register user
        response = self.client.post("/api/v1/users", json=user_data)

        # Then
        assert response.status_code == 201
        result = response.json()
        assert (
            result["message"]
            == "User registered successfully. Check your email for activation code."
        )
        assert "user_id" in result

        # Step 2: Try to access protected endpoint before activation (should fail)
        auth_header = self._create_basic_auth_header(user_data["email"], user_data["password"])
        response = self.client.get("/api/v1/users/me", headers={"Authorization": auth_header})

        assert response.status_code == 401

        # Step 3: Get activation code (in real app, this would be from email)
        # For integration tests, we use PostgreSQL explicitly
        from src.di.container import AppContainer

        container = AppContainer(use_postgresql=True, use_mock_email=True)
        activation_repo = container.activation_code_repository()

        # Get user ID from registration response
        user_id = result["user_id"]
        activation_code = activation_repo.get_by_user_id(user_id)
        assert activation_code is not None

        # Step 4: Activate account with new RESTful endpoint (using dummy user_id)
        activation_data = {"activation_code": activation_code.code}
        response = self.client.patch(f"/api/v1/users/{user_id}", json=activation_data)

        assert response.status_code == 200
        assert response.json()["message"] == "Account activated successfully."

        # Step 5: Now access protected endpoint (should succeed)
        response = self.client.get("/api/v1/users/me", headers={"Authorization": auth_header})

        assert response.status_code == 200
        user_info = response.json()
        assert user_info["email"] == user_data["email"]
        assert user_info["is_active"] is True

    def test_duplicate_registration_security(self):
        """Test that duplicate registrations don't reveal user existence."""
        # Given
        unique_email = f"duplicate-{uuid.uuid4().hex[:8]}@example.com"
        user_data = {"email": unique_email, "password": "password123"}

        # First registration
        response1 = self.client.post("/api/v1/users", json=user_data)
        assert response1.status_code == 201

        # Second registration with same email
        response2 = self.client.post("/api/v1/users", json=user_data)

        # Should return same response (security measure)
        assert response2.status_code == 201
        assert (
            response2.json()["message"]
            == "User registered successfully. Check your email for activation code."
        )

    def test_invalid_activation_code(self):
        """Test activation with invalid code."""
        # Given
        invalid_data = {"activation_code": "9999"}

        # When - using dummy user ID since we don't have a real one
        response = self.client.patch("/api/v1/users/dummy-id", json=invalid_data)

        # Then
        assert response.status_code == 400
        assert "Invalid activation code" in response.json()["detail"]

    def test_expired_activation_code(self):
        """Test that expired activation codes are rejected."""
        # Given
        unique_email = f"expired-{uuid.uuid4().hex[:8]}@example.com"
        user_data = {"email": unique_email, "password": "password123"}
        response = self.client.post("/api/v1/users", json=user_data)
        user_id = response.json()["user_id"]

        # Get and manually expire the activation code
        from src.di.container import AppContainer

        container = AppContainer(use_postgresql=True, use_mock_email=True)
        activation_repo = container.activation_code_repository()

        activation_code = activation_repo.get_by_user_id(user_id)
        assert activation_code is not None

        # Expire the code in database
        import datetime

        from src.persistances.db import get_db_cursor

        expired_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=1)
        with get_db_cursor() as cursor:
            cursor.execute(
                "UPDATE activation_codes SET expires_at = %s WHERE user_id = %s",
                (expired_time, user_id),
            )

        # When - try to activate with expired code
        activation_data = {"activation_code": activation_code.code}
        response = self.client.patch(f"/api/v1/users/{user_id}", json=activation_data)

        # Then
        assert response.status_code == 400
        assert "expired" in response.json()["detail"].lower()

    def test_authentication_endpoints(self):
        """Test authentication with various scenarios."""
        # Setup: Create and activate user
        unique_email = f"auth-{uuid.uuid4().hex[:8]}@example.com"
        user_data = {"email": unique_email, "password": "password123"}
        response = self.client.post("/api/v1/users", json=user_data)
        user_id = response.json()["user_id"]

        # Activate user
        from src.di.container import AppContainer

        container = AppContainer(use_postgresql=True, use_mock_email=True)
        activation_repo = container.activation_code_repository()
        activation_code = activation_repo.get_by_user_id(user_id)
        assert activation_code is not None

        activation_data = {"activation_code": activation_code.code}
        self.client.patch(f"/api/v1/users/{user_id}", json=activation_data)

        # Test 1: Valid authentication
        auth_header = self._create_basic_auth_header(user_data["email"], user_data["password"])
        response = self.client.get("/api/v1/users/me", headers={"Authorization": auth_header})
        assert response.status_code == 200

        # Test 2: Invalid password
        wrong_auth = self._create_basic_auth_header(user_data["email"], "wrong_password")
        response = self.client.get("/api/v1/users/me", headers={"Authorization": wrong_auth})
        assert response.status_code == 401

        # Test 3: Non-existent user
        # Test with fake credentials
        fake_email = f"fake-{uuid.uuid4().hex[:8]}@example.com"
        fake_auth = self._create_basic_auth_header(fake_email, "password")
        response = self.client.get("/api/v1/users/me", headers={"Authorization": fake_auth})
        assert response.status_code == 404

        # Test 4: Malformed auth header
        response = self.client.get("/api/v1/users/me", headers={"Authorization": "Invalid Header"})
        assert response.status_code == 401

    def test_api_error_responses(self):
        """Test API error handling and response formats."""
        # Test 1: Invalid JSON
        response = self.client.post(
            "/api/v1/users", content="invalid json", headers={"content-type": "application/json"}
        )
        assert response.status_code == 422

        # Test 2: Missing fields
        # Test missing password
        test_email = f"test-{uuid.uuid4().hex[:8]}@example.com"
        response = self.client.post("/api/v1/users", json={"email": test_email})
        assert response.status_code == 422

        # Test 3: Invalid email format
        response = self.client.post(
            "/api/v1/users", json={"email": "invalid-email", "password": "pass"}
        )
        assert response.status_code == 422

        # Test 4: Missing activation code
        response = self.client.patch("/api/v1/users/dummy-id", json={})
        assert response.status_code == 422

    def test_one_minute_expiration_requirement(self):
        """Test the specific 1-minute expiration requirement from client specs."""
        # Given - register user
        unique_email = f"timing-{uuid.uuid4().hex[:8]}@example.com"
        user_data = {"email": unique_email, "password": "password123"}
        start_time = time.time()

        response = self.client.post("/api/v1/users", json=user_data)
        user_id = response.json()["user_id"]

        # Get activation code timing
        from src.di.container import AppContainer

        container = AppContainer(use_postgresql=True, use_mock_email=True)
        activation_repo = container.activation_code_repository()

        activation_code = activation_repo.get_by_user_id(user_id)
        assert activation_code is not None
        assert activation_code.expires_at is not None

        # Calculate expected expiration (should be 1 minute from creation)
        creation_time = activation_code.created_at.timestamp()
        expected_expiry = creation_time + 60  # 1 minute = 60 seconds
        actual_expiry = activation_code.expires_at.timestamp()

        # Verify timing (allow 1 second tolerance for test execution)
        time_difference = abs(actual_expiry - expected_expiry)
        assert (
            time_difference < 1
        ), f"Expiration should be 1 minute, but difference is {time_difference} seconds"

        # Verify the code is valid immediately
        assert not activation_code.is_expired

    def _create_basic_auth_header(self, email: str, password: str) -> str:
        """Helper to create Basic Auth header."""
        credentials = base64.b64encode(f"{email}:{password}".encode()).decode()
        return f"Basic {credentials}"


class TestAPIDocumentation:
    """Tests for API documentation and OpenAPI spec."""

    def setup_method(self):
        """Setup client."""
        self.client = TestClient(app)

    def test_openapi_documentation_available(self):
        """Test that OpenAPI documentation is available."""
        # Test OpenAPI JSON
        response = self.client.get("/openapi.json")
        assert response.status_code == 200

        openapi_spec = response.json()
        assert "openapi" in openapi_spec
        assert "info" in openapi_spec
        assert openapi_spec["info"]["title"] == "Simple Auth API"

        # Verify required endpoints are documented
        paths = openapi_spec["paths"]
        assert "/api/v1/users" in paths
        assert "/api/v1/users/me" in paths
        assert "/api/v1/health" in paths

    def test_swagger_ui_available(self):
        """Test that Swagger UI is available."""
        response = self.client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


if __name__ == "__main__":
    # Run integration tests with: python -m pytest tests/test_integration.py -v
    import pytest

    pytest.main([__file__, "-v"])

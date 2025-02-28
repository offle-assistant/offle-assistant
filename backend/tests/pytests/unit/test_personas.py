import asyncio

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from offle_assistant.main import app
from offle_assistant.auth import (
    # get_current_user,
    builder_required,
)

client = TestClient(app)


# THIS CODE IS CURRENTLY MOSTLY NON-FUNCTIONAL,
# BUT IT HAS SOME GROUNDWORK FOR FUTURE TESTING.


def override_get_current_user():
    # Mocks a builder user
    class MockUser:
        id = "63e4bcf5a79a8402ad3bb03b"
        role = "user"
        email = "test@example.com"
        hashed_password = "fake_hash"
    return MockUser()


def override_builder_required():
    """Return a mock user with the 'builder' role, bypassing real auth."""
    class MockUser:
        id = "63e4bcf5a79a8402ad3bb03b"
        role = "builder"
        email = "test@example.com"
        hashed_password = "fake_hash"
    return MockUser()


@pytest.fixture
def setup_override():
    # Override the dependency that requires a builder or admin
    app.dependency_overrides[builder_required] = override_builder_required
    yield
    app.dependency_overrides = {}


def test_create_persona_success(setup_override):
    """
    Mocks get_user_by_id so the user is found in the 'database',
    then tests the create_persona endpoint.
    """

    payload = {
        "name": "TestName",
        "description": "Test Description",
        "system_prompt": "You are a helpful AI assistant.",
        "model": "llama3.2",
        "temperature": 0.7
    }

    response = client.post("/personas/build", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Persona created successfully"
    assert "persona_id" in data


@patch("offle_assistant.database.get_persona_by_id", new_callable=AsyncMock)
@patch("offle_assistant.database.update_persona_in_db", new_callable=AsyncMock)
def test_update_persona_success(setup_override):
    payload = {
        "name": "TestName",
        "description": "Test Description",
        "system_prompt": "You are a helpful AI assistant.",
        "model": "llama3.2",
        "temperature": 0.7
    }

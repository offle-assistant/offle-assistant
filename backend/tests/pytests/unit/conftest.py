import pytest

from offle_assistant.auth import (
    get_current_user,
    builder_required,
)

from offle_assistant.main import app

from offle_assistant.mongo import db


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


@pytest.fixture(autouse=True)
async def cleanup_db():
    # Clean up before the test
    await db.client.drop_database(db.name)
    yield
    # Clean up after the test
    await db.client.drop_database(db.name)


@pytest.fixture
def setup_builder_override():
    # Override the dependency that requires a builder or admin
    app.dependency_overrides[builder_required] = override_builder_required
    yield
    app.dependency_overrides = {}


@pytest.fixture
def setup_user_override():
    # Override the dependency that requires a builder or admin
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides = {}

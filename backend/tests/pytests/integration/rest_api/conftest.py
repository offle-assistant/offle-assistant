from httpx import AsyncClient, ASGITransport

import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from offle_assistant.main import app
from offle_assistant.dependencies import get_db
from offle_assistant.mongo import MONGO_URI
from offle_assistant.models import UserModel, PyObjectId


@pytest.fixture(scope="function")
def override_get_current_user_normal_user():
    """Override authentication to always return a test user."""
    user_id = PyObjectId()

    async def mock_get_current_user():
        return UserModel(
            _id=str(user_id),
            username="test",
            email="test@example.com",
            hashed_password="hashedpassword",
        )

    return mock_get_current_user


@pytest.fixture(scope="function")
def override_get_current_user_builder():
    """Override authentication to always return a test builder."""
    user_id = PyObjectId()

    async def mock_get_current_user():
        return UserModel(
            _id=str(user_id),
            username="test",
            email="test@example.com",
            hashed_password="hashedpassword",
            role="builder"
        )

    return mock_get_current_user


@pytest.fixture(scope="function")
def override_get_current_user_admin():
    """Override authentication to always return a test admin."""
    user_id = PyObjectId()

    async def mock_get_current_user():
        return UserModel(
            _id=str(user_id),
            username="test",
            email="test@example.com",
            hashed_password="hashedpassword",
            role="admin"
        )

    return mock_get_current_user


@pytest_asyncio.fixture
async def test_db():
    """Creates a test MongoDB database session."""
    client = AsyncIOMotorClient(
        MONGO_URI,
        uuidRepresentation="standard",
    )
    mock_db = client["test_database"]
    yield mock_db

    client.drop_database(mock_db.name)
    client.close()


@pytest_asyncio.fixture
async def test_client(
    test_db,
):
    """Overrides the FastAPI dependency and returns a test client."""

    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()  # Cleanup after tests

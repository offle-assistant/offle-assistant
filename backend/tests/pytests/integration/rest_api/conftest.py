from httpx import AsyncClient, ASGITransport

import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from offle_assistant.main import app
from offle_assistant.dependencies import get_db
from offle_assistant.mongo import MONGO_USER, MONGO_PASSWORD
from offle_assistant.models import UserModel, PyObjectId
from offle_assistant.auth import get_current_user


@pytest.fixture(scope="function")
def override_get_current_user():
    """Override authentication to always return a test user."""
    async def mock_get_current_user():
        return UserModel(
            id=str(PyObjectId()),
            username="test",
            email="test@example.com",
            hashed_password="hashedpassword",
        )

    return mock_get_current_user


@pytest_asyncio.fixture
async def test_db():
    """Creates a test MongoDB database session."""
    MONGO_URI = (
        f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@"
        "localhost:27017/test_database?authSource=admin"
    )
    client = AsyncIOMotorClient(
        MONGO_URI,
        uuidRepresentation="standard",
    )
    mock_db = client["test_database"]

    yield mock_db  # Ensure you're yielding the actual database instance

    client.close()


@pytest_asyncio.fixture
async def test_client(test_db, override_get_current_user):
    """Overrides the FastAPI dependency and returns a test client."""

    async def override_get_db():
        yield test_db  # Ensure this yields the correct database instance

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()  # Cleanup after tests

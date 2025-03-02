import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket

from offle_assistant.mongo import MONGO_URI


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


@pytest_asyncio.fixture(scope="function")
async def test_fs_bucket(test_db):
    """Provides a fresh GridFS bucket for each test."""
    return AsyncIOMotorGridFSBucket(test_db)

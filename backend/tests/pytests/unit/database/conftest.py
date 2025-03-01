import pytest
import asyncio
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
# from pymongo import MongoClient
# from app.models import FileMetadata  # Import your Pydantic model


# Test database URI (use a separate test DB)
TEST_MONGO_URI = "mongodb://localhost:27017"
TEST_DB_NAME = "test_database"


@pytest_asyncio.fixture(scope="session")
async def test_db():
    """Creates a test MongoDB database and GridFS bucket"""
    client = AsyncIOMotorClient(TEST_MONGO_URI)
    db = client[TEST_DB_NAME]
    fs_bucket = AsyncIOMotorGridFSBucket(db)

    yield db, fs_bucket  # Provide database and GridFS instance

    # Cleanup after test session
    await db.drop_collection("fs.files")
    await db.drop_collection("fs.chunks")
    await client.drop_database(TEST_DB_NAME)

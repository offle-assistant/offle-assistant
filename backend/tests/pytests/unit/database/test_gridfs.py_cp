import pytest
# import asyncio
import mimetypes
from bson import ObjectId
from offle_assistant.models import FileMetadata
import pathlib


TEST_DIR = pathlib.Path("./test_data/")
TEST_FILE = pathlib.Path(TEST_DIR, "test_file.txt")


@pytest.mark.asyncio
async def upload_test_file(
    fs_bucket,
    filename=TEST_FILE,
    content=b"Hello, GridFS!"
):
    """Helper function to upload a test file"""
    mime_type, _ = mimetypes.guess_type(filename)
    metadata = FileMetadata(
        filename=filename,
        uploaded_by="test_user",
        content_type=mime_type or "application/octet-stream",
        description="Test file",
        tags=["test"]
    )
    file_id = await fs_bucket.upload_from_stream(
        filename, content, metadata=metadata.dict()
    )
    return file_id


@pytest.mark.asyncio
async def test_upload_file(test_db):
    """Test uploading a file to GridFS"""
    db, fs_bucket = test_db
    file_id = await upload_test_file(fs_bucket)

    assert isinstance(file_id, ObjectId)

    file_doc = await db.fs.files.find_one({"_id": file_id})
    assert file_doc is not None
    assert file_doc["metadata"]["filename"] == "test_file.txt"
    assert file_doc["metadata"]["uploaded_by"] == "test_user"


@pytest.mark.asyncio
async def test_retrieve_metadata(test_db):
    """Test retrieving metadata from GridFS"""
    db, fs_bucket = test_db
    file_id = await upload_test_file(fs_bucket)

    file_doc = await db.fs.files.find_one({"_id": file_id})
    assert file_doc is not None

    metadata = FileMetadata(**file_doc["metadata"])
    assert metadata.filename == "test_file.txt"
    assert metadata.content_type == "text/plain"


@pytest.mark.asyncio
async def test_download_file(test_db):
    """Test downloading a file from GridFS"""
    db, fs_bucket = test_db
    file_id = await upload_test_file(fs_bucket, content=b"Test content")

    file_stream = await fs_bucket.open_download_stream(file_id)
    file_data = await file_stream.read()

    assert file_data == b"Test content"


@pytest.mark.asyncio
async def test_delete_file(test_db):
    """Test deleting a file from GridFS"""
    db, fs_bucket = test_db
    file_id = await upload_test_file(fs_bucket)

    await fs_bucket.delete(file_id)

    file_doc = await db.fs.files.find_one({"_id": file_id})
    assert file_doc is None

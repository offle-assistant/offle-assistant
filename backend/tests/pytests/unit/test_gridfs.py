import pytest
from offle_assistant.crud import upload_file, download_file
from bson import ObjectId


@pytest.mark.asyncio
async def test_upload_and_download_file(test_db, test_fs_bucket):
    """Test uploading and downloading a file in GridFS"""
    filename = "test.txt"
    content = b"Hello, GridFS!"

    # Upload file
    file_id = await upload_file(test_db, filename, content, "test_user")
    assert isinstance(file_id, ObjectId)

    # Download file
    file_content = await download_file(test_db, file_id)
    assert file_content == content

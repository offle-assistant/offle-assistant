import pathlib
import hashlib

import pytest
from bson import ObjectId

from offle_assistant.database import upload_file, download_file, delete_file
from offle_assistant.models import FileMetadata


TEST_DIR = pathlib.Path("./test_data")
TEST_FILE = pathlib.Path(TEST_DIR, "test_file.txt")

OUTPUT_PATH = pathlib.Path(TEST_DIR, "downloaded.txt")


def hash_file(filepath: str) -> str:
    """Returns the SHA-256 hash of a file"""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()


def files_are_identical(
    file_a: pathlib.Path,
    file_b: pathlib.Path
) -> bool:
    return hash_file(file_a) == hash_file(file_b)


@pytest.mark.asyncio
async def test_upload_and_download_file(
    test_db,
    test_fs_bucket,
):
    """Test uploading and downloading a file in GridFS"""
    filename = "test.txt"

    file_metadata: FileMetadata = FileMetadata(
        filename=filename,
        version=1,
        uploaded_by="Ricardo Mutti",
        description="A brief history of the Chicago Symphony."
    )

    # Upload file
    file_id = await upload_file(
        filepath=TEST_FILE,
        metadata=file_metadata,
        db=test_db
    )

    assert isinstance(file_id, ObjectId)

    # Download file
    content = await download_file(
        file_id=file_id,
        output_path=OUTPUT_PATH,
        db=test_db
    )

    assert files_are_identical(TEST_FILE, OUTPUT_PATH)
    assert content is not None  # This test sucks


@pytest.mark.asyncio
async def test_upload_and_delete_file(
    test_db,
    test_fs_bucket,
):
    """Test uploading and downloading a file in GridFS"""
    filename = "test.txt"

    file_metadata: FileMetadata = FileMetadata(
        filename=filename,
        version=1,
        uploaded_by="Ricardo Mutti",
        description="A brief history of the Chicago Symphony."
    )

    # Upload file
    file_id = await upload_file(
        filepath=TEST_FILE,
        metadata=file_metadata,
        db=test_db
    )

    assert isinstance(file_id, ObjectId)

    success = await delete_file(
        file_id=file_id,
        db=test_db
    )

    assert success is True

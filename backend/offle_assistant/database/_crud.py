import logging

from fastapi.responses import StreamingResponse
from fastapi import UploadFile
from bson import ObjectId
from motor.motor_asyncio import (
    AsyncIOMotorGridFSBucket,
    AsyncIOMotorDatabase
)

from offle_assistant.models import (
    FileMetadata
)


async def upload_file(
    file: UploadFile,
    metadata: FileMetadata,
    db: AsyncIOMotorDatabase
):
    fs_bucket = AsyncIOMotorGridFSBucket(db)

    file_id = await fs_bucket.upload_from_stream(
        filename=file.filename,
        source=file.file,
        metadata=metadata
    )

    logging.info("File uploaded with id: %s", str(file_id))

    return str(file_id)


async def download_file(
    file_id,
    output_path: str,
    db: AsyncIOMotorDatabase
):
    """API Endpoint to download a file from GridFS"""
    fs_bucket = AsyncIOMotorGridFSBucket(db)
    stream = await fs_bucket.open_download_stream(ObjectId(file_id))

    return StreamingResponse(
        stream, media_type="application/octet-stream", headers={
            "Content-Disposition": f'attachment; filename="{file_id}"'
        }
    )


async def delete_file(
    file_id,
    db: AsyncIOMotorDatabase
):
    fs_bucket = AsyncIOMotorGridFSBucket(db)

    # Check if the file exists before attempting deletion
    file_doc = await db["fs.files"].find_one({"_id": ObjectId(file_id)})

    if not file_doc:
        logging.warning("File with ID %s not found in GridFS.", file_id)
        return False  # File was not found

    # Delete the file
    await fs_bucket.delete(ObjectId(file_id))

    # Confirm the file has been deleted
    file_check = await db["fs.files"].find_one({"_id": ObjectId(file_id)})

    if file_check:
        logging.error("File with ID %s was not deleted successfully.", file_id)
        return False  # File still exists (unexpected)

    logging.info("File with ID %s deleted successfully.", file_id)
    return True  # File was deleted successfully

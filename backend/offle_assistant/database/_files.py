import logging

from bson import ObjectId
from fastapi.responses import StreamingResponse
from fastapi import UploadFile
from motor.motor_asyncio import (
    AsyncIOMotorGridFSBucket,
    AsyncIOMotorDatabase
)

from offle_assistant.models import (
    FileMetadata,
)


############################
# CREATE
############################


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


############################
# RETRIEVE
############################

async def get_file_metadata(
    file_id,
    db: AsyncIOMotorDatabase
):
    """Retrieve metadata of a file in GridFS"""
    file_doc = await db.fs.files.find_one({"_id": file_id})
    if file_doc:
        metadata = FileMetadata(**file_doc["metadata"])
        logging.info("File Metadata: %s", metadata)
        return metadata
    else:
        logging.info("File not found")
        return None


async def find_files_by_tag(
        tag: str,
        db: AsyncIOMotorDatabase
):
    """Find files with a specific tag"""
    cursor = db.fs.files.find({"metadata.tags": tag})
    results = await cursor.to_list(length=100)
    return results


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


############################
# UPDATE
############################

############################
# DELETE
############################


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

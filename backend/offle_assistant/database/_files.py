import mimetypes
import logging
from typing import List

from bson import ObjectId
from fastapi.responses import StreamingResponse
from fastapi import (
    UploadFile,
)
from motor.motor_asyncio import (
    AsyncIOMotorGridFSBucket,
    AsyncIOMotorDatabase
)

from offle_assistant.models import (
    FileMetadata,
    GroupModel
)
import offle_assistant.database as database


############################
# CREATE
############################


async def upload_file(
    file: UploadFile,
    description: str,
    groups: list,
    tags: List[str],
    user_id: str,
    user_groups: List[str],
    db: AsyncIOMotorDatabase
):
    # Ensure at least one group exists
    if not groups:
        default_group_dict = await database.get_default_group(db)
        default_group: GroupModel = GroupModel(**default_group_dict)
        groups.append(default_group.name)

    fs_bucket = AsyncIOMotorGridFSBucket(db)

    # Double check that the content type passed through is correct/best
    content_type = file.content_type
    if not content_type or content_type == "application/octet-stream":
        guessed_type, _ = mimetypes.guess_type(file.filename)
        content_type = (
            guessed_type if guessed_type else "application/octet-stream"
        )

    user_groups: List[str] = user_groups

    # Nifty way of seeing if there is a common member between 2 lists
    has_permission = bool(set(groups) & set(user_groups))

    if not has_permission:
        raise PermissionError

    file_metadata = FileMetadata(
        filename=file.filename,
        uploaded_by=user_id,
        content_type=content_type,
        description=description,
        tags=tags,
        groups=groups
    )

    file_metadata_dict = file_metadata.model_dump()

    file_id = await fs_bucket.upload_from_stream(
        filename=file.filename,
        source=file.file,
        metadata=file_metadata_dict
    )

    logging.info("File uploaded with id: %s", str(file_id))

    return str(file_id)


############################
# RETRIEVE
############################

async def get_file_metadata_by_id(
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


async def download_file_by_id(
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


async def delete_file_by_id(
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

from typing import Optional
import logging

from fastapi.responses import StreamingResponse
from fastapi import UploadFile
from bson import ObjectId
from motor.motor_asyncio import (
    AsyncIOMotorGridFSBucket,
    AsyncIOMotorDatabase
)
from pymongo.results import UpdateResult

from offle_assistant.models import (
    GroupModel,
    MessageHistoryModel,
    MessageContent,
    FileMetadata
)

from ._queries import (
    get_message_history_entry_by_id
)


async def create_group(
    group: GroupModel,
    db: AsyncIOMotorDatabase
) -> ObjectId:
    """
        Adds a new group to the database. Returns the new id
    """
    result = await db.groups.insert_one(
        group.model_dump(exclude={"id"})
    )
    return result.inserted_id


async def delete_group(
    group_id: str,
    db: AsyncIOMotorDatabase
) -> UpdateResult:
    """Deletes a user by id."""
    return await db.groups.delete_one({"_id": ObjectId(group_id)})


async def update_group(
    group_id: str,
    updates: dict,
    db: AsyncIOMotorDatabase
) -> UpdateResult:
    updated = await db.groups.update_one(
        {"_id": ObjectId(group_id)},
        {"$set": updates}
    )

    return updated


async def create_message_history_entry_in_db(
    db: AsyncIOMotorDatabase,
    new_message_history_entry: Optional[MessageHistoryModel] = None,
) -> ObjectId:
    if new_message_history_entry is None:
        new_message_history_entry = MessageHistoryModel(
            title="Default Title",
            description="Default Description",
        )

    result = await db.message_histories.insert_one(
        new_message_history_entry.model_dump(exclude={"id"})
    )
    return result.inserted_id


async def update_message_history_entry_in_db(
    message_history_id: str,
    updates: dict,
    db: AsyncIOMotorDatabase
) -> UpdateResult:
    update_success = await db.message_histories.update_one(
        {"_id": ObjectId(message_history_id)},
        {"$set": updates}
    )
    return update_success


async def append_message_to_message_history_entry_in_db(
    message_history_id: str,
    message: MessageContent,
    db: AsyncIOMotorDatabase
):
    message_history_entry: MessageHistoryModel = (
        await get_message_history_entry_by_id(
            message_history_id=message_history_id,
            db=db
        )
    )

    message_history_entry["messages"].append(message.model_dump())
    success = await update_message_history_entry_in_db(
        message_history_id=message_history_id,
        updates=message_history_entry,
        db=db
    )

    return success


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

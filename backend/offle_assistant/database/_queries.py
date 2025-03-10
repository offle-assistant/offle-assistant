import logging

from motor.motor_asyncio import AsyncIOMotorDatabase

from offle_assistant.models import (
    FileMetadata,
)


async def get_admin_exists(db: AsyncIOMotorDatabase) -> bool:
    admin_user = await db.users.find_one({"role": "admin"})
    if admin_user:
        return True
    else:
        return False


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

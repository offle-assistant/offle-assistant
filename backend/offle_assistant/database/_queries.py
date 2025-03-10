import logging
from typing import Dict, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from offle_assistant.models import (
    FileMetadata,
    MessageHistoryModel
)


async def get_admin_exists(db: AsyncIOMotorDatabase) -> bool:
    admin_user = await db.users.find_one({"role": "admin"})
    if admin_user:
        return True
    else:
        return False


async def get_message_history_entry_by_id(
    message_history_id: str,
    db: AsyncIOMotorDatabase
) -> Optional[Dict]:
    """Get a message history object"""
    return await db.message_histories.find_one(
        {"_id": ObjectId(message_history_id)}
    )


async def get_message_history_entry_without_message_chain(
    message_history_id: str,
    db: AsyncIOMotorDatabase
) -> Optional[Dict]:
    """

    Get a message history object but without the message chain.
    This is basically a lightweight version of
    get_message_history_entry_by_id()

    """

    query = {"_id": ObjectId(message_history_id)}
    projection = {"messages": 0}
    retrieved_message_history: dict = await db.message_histories.find_one(
        query,
        projection
    )

    if not retrieved_message_history:
        return None

    return MessageHistoryModel(**retrieved_message_history)


async def get_message_history_list_by_user_id(
    user_id: str,
    persona_id: str,
    db: AsyncIOMotorDatabase
) -> Optional[Dict]:
    """
        Get message history information between a given persona
        and a given user. This omits the actual message chain
        to avoid pulling huge amounts of text all at once. After
        the user decides which message chain they want to pick
        back up with, you can use get_message_history_entry_by_id
        to get the full message history chain for that id.

        This will return None if there is no history to retrieve
    """
    query = {"_id": ObjectId(user_id)}
    projection = {f"persona_message_history.{persona_id}": 1}

    # This returns the user with only the persona_message_history key
    retrieved_user: list = await db.users.find_one(
        query,
        projection
    )
    if not retrieved_user:
        # Couldn't find a user by that id.
        return None

    message_history = retrieved_user.get(
        "persona_message_history",
        {}
    ).get(persona_id, [])

    return message_history


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

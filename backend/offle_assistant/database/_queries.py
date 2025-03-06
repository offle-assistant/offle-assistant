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


async def get_user_by_id(
    user_id: str,
    db: AsyncIOMotorDatabase
) -> Optional[Dict]:
    """Fetch a user from the database by their _id."""
    return await db.users.find_one({"_id": ObjectId(user_id)})


DEFAULT_GROUP_NAME = "default"


async def get_default_group(db: AsyncIOMotorDatabase):
    """Fetch the default group, or create it if it doesn't exist."""
    group = await db.groups.find_one({"name": DEFAULT_GROUP_NAME})

    if not group:
        # Create default group if it doesn't exist
        group_data = {
            "name": DEFAULT_GROUP_NAME,
            "description": "Default group for all users"
        }
        insert_result = await db.groups.insert_one(group_data)
        group = {**group_data, "_id": insert_result.inserted_id}

    return group


async def get_group_by_id(
    group_id: str,
    db: AsyncIOMotorDatabase
) -> Optional[Dict]:
    """Fetch a user from the database by their _id."""
    return await db.groups.find_one({"_id": ObjectId(group_id)})


async def get_group_by_name(
    group_name: str,
    db: AsyncIOMotorDatabase
) -> Optional[Dict]:
    """Fetch a user from the database by their _id."""
    return await db.groups.find_one({"name": group_name})


async def get_user_by_email(
    user_email: str,
    db: AsyncIOMotorDatabase
) -> Optional[Dict]:
    """Fetch a user from the database by their _id."""
    return await db.users.find_one({"email": user_email})


async def get_persona_by_id(
    persona_id: str,
    db: AsyncIOMotorDatabase
) -> Optional[Dict]:
    """Fetch a persona from the database by their _id."""
    return await db.personas.find_one({"_id": ObjectId(persona_id)})


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


async def get_personas_by_creator_id(
    user_id: str,
    db: AsyncIOMotorDatabase
) -> Dict[str, str]:
    """
        Fetch all personas owned by a given user
        and return as {persona_id: persona_name}.
    """

    try:
        user_id = ObjectId(user_id)
    except Exception as e:
        logging.error("%s", e)
        raise ValueError(f"Invalid user_id format: {user_id}")

    # Find all personas where the creator_id matches the user's _id
    personas = await db.personas.find(
        {"creator_id": ObjectId(user_id)}
    ).to_list(None)

    # Convert the result to a dictionary {persona_id: persona_name}
    persona_dict = {
        str(persona["_id"]): persona["name"] for persona in personas
    }

    return persona_dict


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

from typing import Optional
import logging

from bson import ObjectId
from motor.motor_asyncio import (
    AsyncIOMotorGridFSBucket,
    AsyncIOMotorDatabase
)
from pymongo.results import UpdateResult

# from offle_assistant.mongo import (
#     personas_collection,
#     users_collection,
#     message_history_collection,
#     fs_bucket
# )
from offle_assistant.models import (
    PersonaModel,
    Role,
    UserModel,
    MessageHistoryModel,
    MessageContent,
    FileMetadata
)

from ._queries import (
    get_message_history_entry_by_id
)


async def create_user_in_db(
    new_user: UserModel,
    db: AsyncIOMotorDatabase
) -> ObjectId:
    """
        Adds a new user to the db. Returns the new id.
    """
    result = await db.users.insert_one(
        new_user.model_dump(exclude={"id"})
    )
    return result.inserted_id


async def delete_user_in_db(
    user_id: str,
    db: AsyncIOMotorDatabase
) -> UpdateResult:
    """Deletes a user by id."""
    return await db.users.delete_one({"_id": ObjectId(user_id)})


async def update_user_role_in_db(
    user_id: str,
    new_role: Role,
    db: AsyncIOMotorDatabase
) -> UpdateResult:
    """Updates a user's role."""
    return await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"role": new_role}}
    )


async def update_user_in_db(
    user_id: str,
    updates: dict,
    db: AsyncIOMotorDatabase
) -> UpdateResult:
    updated = await db.users.update_one(
        {"_id": ObjectId(user_id)},
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

    message_history_entry["messages"].append(message)
    success = await update_message_history_entry_in_db(
        message_history_id=message_history_id,
        updates=message_history_entry,
        db=db
    )

    return success


async def create_persona_in_db(
    persona: PersonaModel,
    creator_id: str,
    db: AsyncIOMotorDatabase
) -> ObjectId:
    """Insert a new persona into the database and return its ID."""

    persona_data = persona.model_dump()
    persona_data["creator_id"] = ObjectId(creator_id)  # Ensure ObjectId format
    persona_data["user_id"] = ObjectId(creator_id)  # Keep consistency

    result = await db.personas.insert_one(persona_data)
    return result.inserted_id


async def update_persona_in_db(
    persona_id: str,
    updates: dict,
    db: AsyncIOMotorDatabase
) -> UpdateResult:
    updated = await db.personas.update_one(
        {"_id": ObjectId(persona_id)},
        {"$set": updates}
    )

    return updated


async def upload_file(
    filepath: str, metadata: FileMetadata, db: AsyncIOMotorDatabase
):
    with open(filepath, "rb") as f:
        file_id = await db.fs_bucket.upload_from_stream(
            filename=metadata.filename,
            source=f,
            metadata=metadata.model_dump()
        )
    logging.info("File uploaded with id: %s", file_id)
    return file_id


async def download_file(
    file_id,
    output_path: str,
    db: AsyncIOMotorDatabase
):
    fs_bucket = AsyncIOMotorGridFSBucket(db)
    with open(output_path, "wb") as f:
        await fs_bucket.download_to_stream(file_id, f)
    logging.info("File downloaded to %s", output_path)


async def delete_file(
    file_id,
    db: AsyncIOMotorDatabase
):
    fs_bucket = AsyncIOMotorGridFSBucket(db)
    await fs_bucket.delete(file_id)
    logging.info("File deleted from GridFS")

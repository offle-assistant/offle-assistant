from typing import Optional

from bson import ObjectId
from pymongo.results import UpdateResult

from offle_assistant.mongo import (
    personas_collection,
    users_collection,
    message_history_collection
)
from offle_assistant.models import (
    PersonaModel,
    Role,
    UserModel,
    MessageHistoryModel
)


async def create_user_in_db(new_user: UserModel) -> ObjectId:
    """
        Adds a new user to the db. Returns the new id.
    """
    result = await users_collection.insert_one(
        new_user.dict(exclude={"id"})
    )
    return result.inserted_id


async def delete_user_in_db(user_id: str) -> UpdateResult:
    """Deletes a user by id."""
    return await users_collection.delete_one({"_id": ObjectId(user_id)})


async def update_user_role_in_db(
    user_id: str,
    new_role: Role
) -> UpdateResult:
    """Updates a user's role."""
    return await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"role": new_role}}
    )


async def create_message_history_entry_in_db(
    new_message_history_entry: Optional[MessageHistoryModel] = None
) -> ObjectId:
    if new_message_history_entry is None:
        new_message_history_entry = MessageHistoryModel(
            title="Default Title",
            description="Default Description",
            # ...any other defaults...
        )

    result = await message_history_collection.insert_one(
        new_message_history_entry.dict(exclude={"id"})
    )
    return result.inserted_id


async def update_message_history_entry_in_db(
    message_history_id: str,
    updates: dict
) -> UpdateResult:
    update_success = await message_history_collection.update_one(
        {"_id": ObjectId(message_history_id)},
        {"$set": updates}
    )
    return update_success


async def create_persona_in_db(
    persona: PersonaModel,
    creator_id: str
) -> ObjectId:
    """Insert a new persona into the database and return its ID."""

    persona_data = persona.dict()
    persona_data["creator_id"] = ObjectId(creator_id)  # Ensure ObjectId format
    persona_data["user_id"] = ObjectId(creator_id)  # Keep consistency

    result = await personas_collection.insert_one(persona_data)
    return result.inserted_id


async def update_persona_in_db(persona_id: str, updates: dict) -> UpdateResult:
    updated = await personas_collection.update_one(
        {"_id": ObjectId(persona_id)},
        {"$set": updates}
    )

    return updated

from typing import Dict, Optional

from bson import ObjectId

from offle_assistant.mongo import (
    personas_collection,
    users_collection,
    message_history_collection
)


async def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Fetch a user from the database by their _id."""
    return await users_collection.find_one({"_id": ObjectId(user_id)})


async def get_user_by_email(user_email: str) -> Optional[Dict]:
    """Fetch a user from the database by their _id."""
    return await users_collection.find_one({"email": user_email})


async def get_persona_by_id(persona_id: str) -> Optional[Dict]:
    """Fetch a persona from the database by their _id."""
    return await personas_collection.find_one({"_id": ObjectId(persona_id)})


async def get_message_history_entry_by_id(
    message_history_id: str
) -> Optional[Dict]:
    """Get a message history object"""
    return await message_history_collection.find_one(
        {"_id": ObjectId(message_history_id)}
    )


async def get_personas_by_creator_id(user_id: str) -> Dict[str, str]:
    """
        Fetch all personas owned by a given user
        and return as {persona_id: persona_name}.
    """

    # Find all personas where the creator_id matches the user's _id
    personas = await personas_collection.find(
        {"creator_id": ObjectId(user_id)}
    ).to_list(None)

    # Convert the result to a dictionary {persona_id: persona_name}
    persona_dict = {
        str(persona["_id"]): persona["name"] for persona in personas
    }

    return persona_dict

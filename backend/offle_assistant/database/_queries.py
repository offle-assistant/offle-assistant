from typing import Dict,List, Optional

from bson import ObjectId

from offle_assistant.mongo import (
    personas_collection,
    users_collection,
    message_history_collection
)


async def get_admin_exists() -> bool:
    admin_user = await users_collection.find_one({"role": "admin"})
    if admin_user:
        return True
    else:
        return False


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


from bson import ObjectId
from typing import List, Dict, Optional

async def get_message_history_list_by_user_id(
    user_id: str,
    persona_id: str
) -> Optional[List[Dict]]:
    query = {"_id": ObjectId(user_id)}
    projection = {f"persona_message_history.{persona_id}": 1}

    retrieved_user = await users_collection.find_one(query, projection)

    if not retrieved_user:
        return None  # No user found

    message_history_ids = retrieved_user.get("persona_message_history", {}).get(persona_id, [])

    if not message_history_ids:
        return []

    # 🔹 Fetch full message objects instead of just IDs
    message_history = await message_history_collection.find(
        {"_id": {"$in": [ObjectId(history_id) for history_id in message_history_ids]}}
    ).to_list(length=None)

    # ✅ Convert `_id` to string for JSON serialization
    for history in message_history:
        history["_id"] = str(history["_id"])  # Convert ObjectId to string

        # ✅ Convert message IDs inside `messages` if they exist
        if "messages" in history and isinstance(history["messages"], list):
            for msg in history["messages"]:
                if "_id" in msg and isinstance(msg["_id"], ObjectId):
                    msg["_id"] = str(msg["_id"])  # Convert message `_id` as well

    return message_history  # Return fully formatted message history


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

from typing import Dict, Optional

from bson import ObjectId

from offle_assistant.mongo import (
    personas_collection,
    users_collection,
)
from offle_assistant.models import PersonaModel


async def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Fetch a user from the database by their _id."""
    return await users_collection.find_one({"_id": ObjectId(user_id)})


async def get_persona_by_id(persona_id: str) -> Optional[Dict]:
    """Fetch a persona from the database by their _id."""
    return await personas_collection.find_one({"_id": ObjectId(persona_id)})


async def get_personas_by_user_id(user_id: str) -> Dict[str, str]:
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


async def create_persona_in_db(persona: PersonaModel, creator_id: str) -> str:
    """Insert a new persona into the database and return its ID."""

    persona_data = persona.dict()
    persona_data["creator_id"] = ObjectId(creator_id)  # Ensure ObjectId format
    persona_data["user_id"] = ObjectId(creator_id)  # Keep consistency

    new_persona = await personas_collection.insert_one(persona_data)

    return str(new_persona.inserted_id)  # Return the persona's MongoDB ID


async def update_persona_in_db(persona_id: str, updates: dict):
    updated = await personas_collection.update_one(
        {"_id": ObjectId(persona_id)},
        {"$set": updates}
    )

    return updated

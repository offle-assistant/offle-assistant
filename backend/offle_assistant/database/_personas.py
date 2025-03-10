import logging
from typing import Dict, Optional

from bson import ObjectId
from motor.motor_asyncio import (
    AsyncIOMotorDatabase
)
from pymongo.results import UpdateResult, DeleteResult

from offle_assistant.models import (
    PersonaModel,
)


############################
# CREATE
############################


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


############################
# Retrieve
############################

async def get_persona_by_id(
    persona_id: str,
    db: AsyncIOMotorDatabase
) -> Optional[Dict]:
    """Fetch a persona from the database by their _id."""
    return await db.personas.find_one({"_id": ObjectId(persona_id)})


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


############################
# Update
############################


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


############################
# Delete
############################


async def delete_persona_by_id(
    persona_id: str,
    db: AsyncIOMotorDatabase
) -> DeleteResult:
    """Deletes a persona by id."""
    return await db.personas.delete_one({"_id": ObjectId(persona_id)})

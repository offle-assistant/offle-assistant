from bson import ObjectId
from pymongo.results import UpdateResult

from offle_assistant.mongo import (
    personas_collection,
    users_collection,
)
from offle_assistant.models import PersonaModel, Role, UserModel


async def create_user_in_db(new_user: UserModel) -> ObjectId:
    """
        Adds a new user to the db. Returns the new id.
    """
    return await users_collection.insert_one(
        new_user.dict(exclude={"id"})
    )


async def create_persona_in_db(
    persona: PersonaModel,
    creator_id: str
) -> str: 
    """Insert a new persona into the database and return its ID as a string."""

    persona_data = persona.dict()
    persona_data["creator_id"] = ObjectId(creator_id) 
    persona_data["user_id"] = ObjectId(creator_id)  

    result = await personas_collection.insert_one(persona_data)  
    return str(result.inserted_id) 

async def update_persona_in_db(persona_id: str, updates: dict) -> UpdateResult:
    updated = await personas_collection.update_one(
        {"_id": ObjectId(persona_id)},
        {"$set": updates}
    )

    return updated


async def delete_user_in_db(user_id: str) -> UpdateResult:
    """Deletes a user by id."""
    return await users_collection.delete_one({"_id": ObjectId(user_id)})


async def update_user_role_in_db(user_id: str, new_role: Role):
    """Updates a user's role."""
    return await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"role": new_role}}
    )

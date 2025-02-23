from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId

from offle_assistant.database import personas_collection, users_collection
from offle_assistant.auth import builder_required, get_current_user
from offle_assistant.models import PersonaModel

personas_router = APIRouter()


@personas_router.get("/owned")
async def get_user_personas(user: dict = Depends(get_current_user)):
    """Returns a dictionary of all personas owned by the logged-in user."""

    user_id = user["_id"]

    # Find all personas where the creator_id matches the user's _id
    personas = await personas_collection.find(
        {"creator_id": ObjectId(user_id)}
    ).to_list(None)

    # Convert the result to a dictionary {persona_id: persona_name}
    persona_dict = {
        str(persona["_id"]): persona["name"] for persona in personas
    }

    return persona_dict


@personas_router.post("/build")
async def create_persona(
    persona: PersonaModel,
    user: dict = Depends(builder_required)
):
    """Allows a builder or admin to create a persona."""

    # Ensure the user exists in the database
    creator_id = user["_id"]
    existing_user = await users_collection.find_one(
        {"_id": ObjectId(creator_id)}
    )

    if not existing_user:
        raise HTTPException(
            status_code=400, detail="Invalid user_id: User does not exist"
        )

    # Attach the creator's user_id to track ownership
    persona_data = persona.dict()
    persona_data["creator_id"] = creator_id
    persona_data["user_id"] = creator_id

    new_persona = await personas_collection.insert_one(persona_data)
    return {
        "message": "Persona created successfully",
        "persona_id": str(new_persona.inserted_id)
    }


@personas_router.put("/build/{persona_id}")
async def update_persona(
    persona_id: str, updates: dict, user: dict = Depends(builder_required)
):
    """
        Allows builders to update their own personas
        and admins to update any persona.
    """

    persona = await personas_collection.find_one({"_id": ObjectId(persona_id)})
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    if user["role"] != "admin" and persona["creator_id"] != user["_id"]:
        raise HTTPException(
            status_code=403, detail="You can only modify your own personas"
        )

    updated = await personas_collection.update_one(
        {"_id": ObjectId(persona_id)},
        {"$set": updates}
    )
    if updated.modified_count == 0:
        raise HTTPException(status_code=400, detail="No changes made")

    return {"message": "Persona updated successfully"}


@personas_router.post("/chat/{persona_id}")
async def chat_with_persona(
    persona_id: str, message: dict, user: dict = Depends(get_current_user)
):
    """Allows any user to chat with a persona."""

    persona = await personas_collection.find_one({"_id": ObjectId(persona_id)})
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    user_message = message.get("content", "")
    if not user_message:
        raise HTTPException(
            status_code=400, detail="Message content is required"
        )

    # Placeholder for now. Eventually this will be a Persona.chat() response.
    bot_response = f"{persona['name']} says: 'Hello, you said: {user_message}'"

    return {"persona_id": persona_id, "response": bot_response}

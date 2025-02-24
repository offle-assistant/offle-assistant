from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId

from offle_assistant.auth import builder_required, get_current_user
from offle_assistant.models import PersonaModel, PersonaUpdateModel
from offle_assistant.database import (
    get_personas_by_user_id,
    get_user_by_id,
    create_persona_in_db,
    get_persona_by_id,
    update_persona_in_db
)

personas_router = APIRouter()


@personas_router.get("/owned")
async def get_user_personas(user: dict = Depends(get_current_user)):
    """Returns a dictionary of all personas owned by the logged-in user."""

    return await get_personas_by_user_id(user["_id"])


from fastapi.responses import JSONResponse

@personas_router.post("/build")
async def create_persona(
    persona: PersonaModel,
    user: dict = Depends(builder_required)
):
    """Allows a builder or admin to create a persona."""
    
    # Ensure the user exists in the database
    creator_id = user["_id"]
    existing_user = await get_user_by_id(creator_id)

    if not existing_user:
        raise HTTPException(
            status_code=400, detail="Invalid user_id: User does not exist"
        )

    persona_id = await create_persona_in_db(persona, creator_id)

    return JSONResponse(
        content={
            "message": "Persona created successfully",
            "persona_id": str(persona_id)
        },
        status_code=201
    )

@personas_router.put("/build/{persona_id}")
async def update_persona(
    persona_id: str,
    updates: PersonaUpdateModel,
    user: dict = Depends(builder_required)
) :
    """
        Allows builders to update their own personas
        and admins to update any persona.
    """

    persona = await get_persona_by_id(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    if user["role"] != "admin" and persona["creator_id"] != user["_id"]:
        raise HTTPException(
            status_code=403, detail="You can only modify your own personas"
        )

    update_data = updates.model_dump(exclude_unset=True)

    update_success = await update_persona_in_db(persona_id, update_data)

    if update_success.modified_count == 0:
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

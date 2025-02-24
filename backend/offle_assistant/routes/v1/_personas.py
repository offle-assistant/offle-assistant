from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from offle_assistant.auth import builder_required, get_current_user
from offle_assistant.models import (
    PersonaModel,
    PersonaUpdateModel,
    UserModel,
    PyObjectId
)
from offle_assistant.persona import Persona
from offle_assistant.database import (
    get_personas_by_creator_id,
    get_user_by_id,
    create_persona_in_db,
    get_persona_by_id,
    update_persona_in_db,
    create_message_history_entry_in_db
)
from offle_assistant.session_manager import SessionManager

personas_router = APIRouter()


@personas_router.get("/owned")
async def get_user_personas(user: UserModel = Depends(get_current_user)):
    """Returns a dictionary of all personas created by the logged-in user."""

    return await get_personas_by_creator_id(user["_id"])


@personas_router.post("/build")
async def create_persona(
    persona: PersonaModel,
    user: UserModel = Depends(builder_required)
):
    """Allows a builder or admin to create a persona."""

    # Ensure the user exists in the database
    creator_id = user.id
    existing_user = await get_user_by_id(creator_id)

    if not existing_user:
        raise HTTPException(
            status_code=400, detail="Invalid user_id: User does not exist"
        )

    persona_id = await create_persona_in_db(persona, creator_id)

    return {
        "message": "Persona created successfully",
        "persona_id": str(persona_id)
    }


@personas_router.put("/build/{persona_id}")
async def update_persona(
    persona_id: str,
    updates: PersonaUpdateModel,
    user_model: UserModel = Depends(builder_required)
):
    """
        Allows builders to update their own personas
        and admins to update any persona.
    """

    persona = await get_persona_by_id(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    if user_model.role != "admin" and persona["creator_id"] != user_model.id:
        raise HTTPException(
            status_code=403, detail="You can only modify your own personas"
        )

    update_data = updates.model_dump(exclude_unset=True)

    update_success = await update_persona_in_db(persona_id, update_data)

    if update_success.modified_count == 0:
        raise HTTPException(status_code=400, detail="No changes made")

    return {"message": "Persona updated successfully"}


# Request body model
class ChatRequest(BaseModel):
    message_history_id: Optional[PyObjectId] = None
    content: str


@personas_router.post("/chat/{persona_id}")
async def chat_with_persona(
        persona_id: PyObjectId,
        chat_request: ChatRequest,
        user_model: UserModel = Depends(get_current_user),
):
    """Allows any user to chat with a persona."""

    user_id = user_model.id

    message_history_id = chat_request.message_history_id
    # Check if there is a provided message_history_id
    if message_history_id is None:
        # If not, create a new entry in the message_history_collection
        message_history_id = await create_message_history_entry_in_db()
        # And then, ensure that there is a key for this persona_id on the user
        user_model.persona_message_history.root.setdefault(persona_id, [])
        # append new message_history_id to persona_id key on user's msg hist
        user_model.persona_message_history.root[persona_id].append(
            message_history_id
        )

    persona: Persona = await SessionManager.get_persona_instance(
        user_id=user_id,
        persona_id=persona_id,
        message_history_id=message_history_id
    )

    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    user_message = chat_request.content
    if not user_message:
        raise HTTPException(
            status_code=400, detail="Message content is required"
        )

    # Placeholder for now. Eventually this will be a Persona.chat() response.
    bot_response = f"{persona.name} says: 'Hello, you said: {user_message}'"

    SessionManager.save_persona_instance(
        user_id=user_id,
        persona_id=persona_id,
        message_history_id=message_history_id,
        persona=persona
    )

    return {"persona_id": persona_id, "response": bot_response}

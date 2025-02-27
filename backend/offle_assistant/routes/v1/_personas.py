from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ValidationError

from offle_assistant.auth import builder_required, get_current_user
from offle_assistant.models import (
    PersonaModel,
    PersonaUpdateModel,
    UserModel,
    PyObjectId
)
from offle_assistant.persona import Persona, PersonaChatResponse
from offle_assistant.database import (
    get_personas_by_creator_id,
    get_user_by_id,
    create_persona_in_db,
    get_persona_by_id,
    update_persona_in_db,
    create_message_history_entry_in_db,
    get_message_history_list_by_user_id
)
from offle_assistant.session_manager import SessionManager
from offle_assistant.llm_client import LLMClient
from offle_assistant.vector_db import (
    VectorDB,
)
from offle_assistant.dependencies import get_vector_db, get_llm_client

personas_router = APIRouter()


@personas_router.get("/owned")
async def get_user_personas(user_model: UserModel = Depends(get_current_user)):
    """Returns a dictionary of all personas created by the logged-in user."""

    # This is a dict {"persona_id": "persona_name"}
    user_personas = await get_personas_by_creator_id(user_model.id)

    return {
        "user_id": user_model.id,
        "persona_dict": user_personas
    }


@personas_router.get("/{persona_id}", response_model=PersonaModel)
async def get_persona(
    persona_id: str,
    user_model: UserModel = Depends(get_current_user)
):
    """Returns a persona by id."""

    persona_dict: dict = await get_persona_by_id(persona_id)
    if not persona_dict:
        raise HTTPException(status_code=404, detail="Persona not found")

    try:
        persona_dict["_id"] = str(persona_dict["_id"])
        persona_dict["creator_id"] = str(persona_dict["creator_id"])
        persona_dict["user_id"] = str(persona_dict["user_id"])
        persona_model: PersonaModel = PersonaModel(**persona_dict)
    except ValidationError as e:
        # Handle or log the validation error as needed
        raise HTTPException(
            status_code=500, detail=f"Invalid persona data in DB: {e}"
        )

    return persona_model


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


@personas_router.get("/message-history/{persona_id}")
async def get_persona_message_history(
    persona_id: str,
    user_model: UserModel = Depends(get_current_user),
):
    user_id = user_model.id
    message_history_list: list = await get_message_history_list_by_user_id(
        user_id=user_id,
        persona_id=persona_id
    )

    return {
        "persona_id": persona_id,
        "user_id": user_id,
        "message_history": message_history_list,
    }


# Request body model
class ChatRequest(BaseModel):
    message_history_id: Optional[PyObjectId] = None
    content: str


@personas_router.post("/chat/{persona_id}")
async def chat_with_persona(
    persona_id: PyObjectId,
    chat_request: ChatRequest,
    user_model: UserModel = Depends(get_current_user),
    llm_client: LLMClient = Depends(get_llm_client),
    vector_db: VectorDB = Depends(get_vector_db)
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

    chat_response: PersonaChatResponse = persona.chat(
        user_response=user_message,
        stream=False,
        perform_rag=False,
        llm_client=llm_client,
        vector_db=vector_db
    )

    SessionManager.save_persona_instance(
        user_id=user_id,
        persona_id=persona_id,
        message_history_id=message_history_id,
        persona=persona
    )

    return {
        "persona_id": persona_id,
        "message_history_id": str(message_history_id),
        "response": chat_response.chat_response,
        "rag_hit": chat_response.rag_response,
    }

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Request
)
from pydantic import BaseModel

from offle_assistant.mongo import users_collection, personas_collection
from offle_assistant.models import User, PersonaModel
from bson import ObjectId

from offle_assistant.persona import Persona, PersonaChatResponse
from offle_assistant.session_manager import SessionManager
from offle_assistant.schemas import (
    UserCreate,
    UserUpdate,
    UserOut,
    PersonaCreateDefault,
    PersonaUpdate,
    PersonaOut
)
from offle_assistant.vector_db import (
    VectorDB,
    # DbReturnObj
)
from offle_assistant.llm_client import LLMClient
from offle_assistant.dependencies import get_vector_db, get_llm_client

router = APIRouter()


########################################################################
# Begin Chat Code
########################################################################


# Request body model
class Chat(BaseModel):
    user_id: str
    persona_config: PersonaModel
    content: str


# POST route
@router.post("/chat")
async def chat_endpoint(
    chat: Chat,
    llm_client: LLMClient = Depends(get_llm_client),
    vector_db: VectorDB = Depends(get_vector_db)
):

    persona: Persona = SessionManager.get_persona(
        chat.user_id,
        chat.persona_config
    )

    chat_response: PersonaChatResponse = persona.chat(
        user_response=chat.content,
        stream=False,
        perform_rag=True,
        llm_client=llm_client,
        vector_db=vector_db
    )
    # response_text = chat_response.chat_response

    SessionManager.save_persona(chat.user_id, persona)

    return chat_response


########################################################################
    # User Updates
    ####################################################################


@router.post("/users/", response_model=UserOut)
async def create_user_endpoint(user: User):
    """Create a new user."""
    existing_user = await users_collection.find_one({"user_id": user.user_id})
    if existing_user:
        raise HTTPException(status_code=400, detail="User ID already exists")

    await users_collection.insert_one(user.dict())
    return {"message": "User created successfully"}


@router.get("/users/{user_id}")
async def get_user(user_id: str):
    """Fetch user details including their personas."""
    user = await users_collection.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user["_id"] = str(user["_id"])  # Convert Mongo ObjectId to string
    return user

########################################################################
    # Persona Updates
    ####################################################################


@router.post("/personas/")
async def create_persona(persona: Persona):
    """Create a new persona linked to a user."""
    user = await users_collection.find_one({"user_id": persona.user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await personas_collection.insert_one(persona.dict())

    # Update user's persona list
    await users_collection.update_one(
        {"user_id": persona.user_id},
        {"$push": {"personas": persona.persona_id}}
    )

    return {"message": "Persona created successfully"}

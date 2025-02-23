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
# Begin database update code
########################################################################


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user():
    # I need to figure out how to handle this :P
    return {"user_id": 3}


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


# @router.delete("/users/{user_id}")
# async def delete_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = db.query(User).filter(User.user_id == user_id).first()
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     db.delete(db_user)
#     db.commit()
#     return {"message": "User deleted successfully"}


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


@router.get("/personas/{user_id}")
async def get_personas(user_id: str):
    """Fetch all personas for a specific user."""
    personas = await personas_collection.find(
        {"user_id": user_id}
    ).to_list(None)
    return personas


# @router.patch("/personas/{persona_id}", response_model=PersonaOut)
# async def update_persona(
#     persona_id: int,
#     persona_update: PersonaUpdate,
#     current_user: dict = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     db_persona = db.query(PersonaModel).filter(
#         PersonaModel.persona_id == persona_id
#     ).first()
# 
#     if not db_persona:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Persona not found"
#         )
# 
#     if db_persona.user_id != current_user["user_id"]:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to update this persona"
#         )
# 
#     if persona_update.persona_name is not None:
#         db_persona.persona_name = persona_update.persona_name
#     if persona_update.persona_config is not None:
#         db_persona.persona_config = persona_update.persona_config.dict()
# 
#     db.commit()
#     db.refresh(db_persona)
# 
#     return db_persona
# 
# 
# @router.delete("/personas/{persona_id}")
# async def delete_persona(
#     persona_id: int,
#     current_user: dict = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     db_persona = db.query(PersonaModel).filter(
#         PersonaModel.persona_id == persona_id
#     ).first()
# 
#     if not db_persona:
#         raise HTTPException(status_code=404, detail="Persona not found")
# 
#     if db_persona.user_id != current_user["user_id"]:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to update this persona"
#         )
# 
#     db.delete(db_persona)
#     db.commit()
#     return {"message": "User deleted successfully"}

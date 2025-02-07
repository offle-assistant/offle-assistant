from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from offle_assistant.database import SessionLocal
from offle_assistant.models import User, Persona
from offle_assistant.persona import Persona, PersonaChatResponse
from offle_assistant.session_manager import SessionManager
from offle_assistant.config import (
    PersonaConfig,
)
from offle_assistant.schemas import (
    UserCreate,
    UserUpdate,
    UserOut
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
    persona_config: PersonaConfig
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
    response_text = chat_response.chat_response

    print(response_text)

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


@router.post("/add-user")
async def add_user_endpoint(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update only the fields provided.
    if user.first_name is not None:
        db_user.first_name = user.first_name
    if user.last_name is not None:
        db_user.last_name = user.last_name
    if user.email is not None:
        db_user.email = user.email

    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}

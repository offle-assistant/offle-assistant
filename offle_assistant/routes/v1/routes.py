from fastapi import APIRouter, Depends
from pydantic import BaseModel

from offle_assistant.persona import Persona, PersonaChatResponse
from offle_assistant.session_manager import SessionManager
from offle_assistant.config import (
    PersonaConfig,
)
from offle_assistant.vector_db import (
    VectorDB,
    # DbReturnObj
)
from offle_assistant.llm_client import LLMClient
from offle_assistant.dependencies import get_vector_db, get_llm_client

router = APIRouter()

persona_cache = {}


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

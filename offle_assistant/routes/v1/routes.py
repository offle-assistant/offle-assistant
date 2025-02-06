from fastapi import APIRouter
from pydantic import BaseModel
import pathlib

from offle_assistant.persona import Persona, PersonaChatResponse
from offle_assistant.config import Config, PersonaConfig
from offle_assistant.vector_db import (
    QdrantDB,
    VectorDB,
    # DbReturnObj
)

router = APIRouter()

bot_cache = {}
qdrant_db: VectorDB = QdrantDB()


# Request body model
class Message(BaseModel):
    content: str


class ConfigPath(BaseModel):
    path: str


# This should really take a persona config dictionary.
@router.post("/create")
async def create_bot_endpoint(config_path: ConfigPath):
    config_path = pathlib.Path(config_path.path).expanduser()
    config = Config(config_path)
    persona_id = "Ralph"
    persona_dict = config.persona_dict
    selected_persona: PersonaConfig = persona_dict[persona_id]

    persona: Persona = Persona(
        persona_id=persona_id,
        name=selected_persona.name,
        description=selected_persona.description,
        db_collections=selected_persona.db_collections,
        vector_db=qdrant_db,
        system_prompt=selected_persona.system_prompt,
        model=selected_persona.model,
        llm_server_hostname=selected_persona.llm_server_hostname,
        llm_server_port=selected_persona.llm_server_port,
    )
    bot_cache["Ralph"] = persona
    return {"response": "hello world"}


# POST route
@router.post("/chat")
async def chat_endpoint(message: Message):
    chat_response: PersonaChatResponse = bot_cache["Ralph"].chat(
        user_response=message.content,
        stream=False,
        perform_rag=False
    )
    response_text = chat_response.chat_response
    print(response_text)
    return {"response": response_text}

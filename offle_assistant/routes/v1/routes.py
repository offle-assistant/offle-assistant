import hashlib

from fastapi import APIRouter
from pydantic import BaseModel

from offle_assistant.persona import Persona, PersonaChatResponse
from offle_assistant.config import (
    PersonaConfig,
    SettingsConfig
)
from offle_assistant.vector_db import (
    QdrantDB,
    VectorDB,
    # DbReturnObj
)

router = APIRouter()

persona_cache = {}
qdrant_db: VectorDB = QdrantDB()

# Not sure if this is how this works
# settings: SettingsConfig = SettingsConfig()


# Request body model
class Message(BaseModel):
    content: str


class LoadPersonaRequest(BaseModel):
    persona_config: PersonaConfig


# This should really take a persona config dictionary.
@router.post("/load-persona")
async def load_persona_endpoint(load_persona_request: LoadPersonaRequest):
    try:
        response = cache_persona(load_persona_request.persona_config)
        return response
    except Exception as e:
        return {"response": f"Exception encountered: {e}"}


def cache_persona(persona_config: PersonaConfig):
    selected_persona: PersonaConfig = persona_config

    qdrant_db: VectorDB = QdrantDB(
        host=selected_persona.vector_db_server.hostname,
        port=selected_persona.vector_db_server.port
    )

    persona: Persona = Persona(
        persona_id=selected_persona.name,
        name=selected_persona.name,
        description=selected_persona.description,
        db_collections=selected_persona.rag.collections,
        vector_db=qdrant_db,
        system_prompt=selected_persona.system_prompt,
        model=selected_persona.model,
        llm_server_hostname=selected_persona.llm_server.hostname,
        llm_server_port=selected_persona.llm_server.port,
    )
    persona_cache[selected_persona.name] = persona
    return {"response": f"Loaded {persona.name}"}


def get_config_hash(config: dict):
    return hashlib.md5(str(config).encode()).hexdigest()


class LoadSettingsRequest(BaseModel):
    settings: SettingsConfig


@router.post("/load-settings")
async def load_settings(load_settings_request: LoadSettingsRequest):
    settings = SettingsConfig(load_settings_request.settings)


# POST route
@router.post("/chat")
async def chat_endpoint(message: Message):
    chat_response: PersonaChatResponse = persona_cache["Ralph"].chat(
        user_response=message.content,
        stream=False,
        perform_rag=False
    )
    response_text = chat_response.chat_response
    print(response_text)
    return {"response": response_text}

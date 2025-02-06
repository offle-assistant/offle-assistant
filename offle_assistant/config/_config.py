import pathlib
from typing import Dict, Optional, List
import sys

# from jsonschema import validate, ValidationError
from pydantic import BaseModel, Field, ValidationError
import yaml


class StrictBaseModel(BaseModel):
    model_config = {"extra": "forbid"}


# ----- Settings-related Models -----
class HistoryConfig(StrictBaseModel):
    save: bool = True
    file: str = "chat_history.json"
    max_entries: int = 1000


class APIConfig(StrictBaseModel):
    provider: str = "openai"
    key_env_var: str = "OPENAI_API_KEY"


class FormattingConfig(StrictBaseModel):
    user_color: str = "cyan"
    persona_color: str = "pink"
    markdown: bool = True
    word_wrap: bool = True
    max_line_length: int = 80


class LLMServerConfig(StrictBaseModel):
    hostname: str = "localhost"
    port: int = 11434


class VectorDbServerConfig(StrictBaseModel):
    hostname: str = "localhost"
    port: int = 6333


class SettingsConfig(StrictBaseModel):
    default_persona: str = "default"
    logging: bool = True
    log_file: str = "chatbot.log"
    history: HistoryConfig = HistoryConfig()
    api: APIConfig = APIConfig()
    formatting: FormattingConfig = FormattingConfig()
    llm_server: LLMServerConfig = LLMServerConfig()
    vector_db_server: VectorDbServerConfig = VectorDbServerConfig()


# ----- Persona-related Models -----
class RAGConfig(StrictBaseModel):
    collections: List[str] = Field(default_factory=list)
    # document: Optional[str] = None
    # related_docs: List[str] = Field(default_factory=list)


class PersonaConfig(StrictBaseModel):
    name: str = "Offie"
    model: str = "llama3.2"
    system_prompt: str = "You are a helpful assistant."
    description: str = "This is the default chatbot."
    llm_server: LLMServerConfig = LLMServerConfig()
    vector_db_server: VectorDbServerConfig = VectorDbServerConfig()
    rag: RAGConfig = RAGConfig()
    # allowed_models: List[str] = Field(default_factory=list)
    # temperature: float = 0.7
    # max_tokens: int = 4096


class OffleConfig(StrictBaseModel):
    personas: Dict[str, PersonaConfig]
    settings: SettingsConfig = SettingsConfig()


class Config:
    def __init__(self, config_path: pathlib.Path):

        config: OffleConfig = load_config(config_path)
        self.global_user_color = config.settings.formatting.user_color
        self.global_persona_color = config.settings.formatting.persona_color

        self.llm_server_hostname = config.settings.llm_server.hostname
        self.llm_server_port = config.settings.llm_server.port

        self.vector_db_server_hostname = (
            config.settings.vector_db_server.hostname
        )
        self.vector_db_server_port = config.settings.vector_db_server.port

        self.persona_dict = {}
        for persona_id in config.personas.keys():
            current_persona = config.personas[persona_id]
            name = current_persona.name
            description = current_persona.description
            system_prompt = current_persona.system_prompt
            model = current_persona.model
            db_collections = current_persona.rag.collections

            llm_server_hostname = (
                current_persona.llm_server.hostname
            )
            llm_server_port = current_persona.llm_server.port
            # vector_db_server_hostname = (
            #     current_persona.vector_db_server.hostname
            # )
            # vector_db_server_port = (
            #     current_persona.vector_db_server.port
            # )

            llm_server = LLMServerConfig(
                hostname=llm_server_hostname,
                port=llm_server_port
            )

            vector_db_server = VectorDbServerConfig(
                hostname=self.vector_db_server_hostname,
                port=self.vector_db_server_port
            )

            rag = RAGConfig(
                collections=db_collections
            )

            persona_config = PersonaConfig(
                name=name,
                model=model,
                system_prompt=system_prompt,
                description=description,
                llm_server=llm_server,
                rag=rag,
                vector_db_server=vector_db_server,
            )

            self.persona_dict[persona_id] = persona_config


def load_config(config_path: pathlib.Path) -> OffleConfig:
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)

    try:
        config = OffleConfig(**data)
        # print("✅ Config is valid!")
        return config
    except ValidationError as e:
        print("❌ Config validation failed: ", e.json(indent=2))
        print(f"Offending config file: {config_path}")
        sys.exit(1)

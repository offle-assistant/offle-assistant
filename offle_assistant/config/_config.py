import pathlib
from typing import Dict, List
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

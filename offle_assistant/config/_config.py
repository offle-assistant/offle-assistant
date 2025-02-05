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
    enabled: bool = False
    collections: List[str] = Field(default_factory=list)
    # document: Optional[str] = None
    # related_docs: List[str] = Field(default_factory=list)


class PersonaConfig(StrictBaseModel):
    name: str = "Offie"
    system_prompt: str = "You are a helpful assistant."
    model: str = "llama3.2"
    llm_server: LLMServerConfig = LLMServerConfig()
    vector_db_server: VectorDbServerConfig = VectorDbServerConfig()
    description: str = "This is the default chatbot."
    # allowed_models: List[str] = Field(default_factory=list)
    # temperature: float = 0.7
    # max_tokens: int = 4096
    rag: RAGConfig = RAGConfig()


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

        """
            The following is a type of interface for the persona dictionary.
            I'm doing it this way in case I ever want to restructure the yaml
            I can decouple parsing the yaml using instantiations of the config
            class to populate values for personas.

            It also allows me to handle empty values before they get to the
            persona class.

        """
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

            persona_config = PersonaConfig(
                persona_id=persona_id,
                name=name,
                description=description,
                system_prompt=system_prompt,
                model=model,
                db_collections=db_collections,
                llm_server_hostname=llm_server_hostname,
                llm_server_port=llm_server_port
            )

            self.persona_dict[persona_id] = persona_config


class PersonaConfig:
    def __init__(
        self,
        persona_id: str,
        name: str,
        description: str,
        system_prompt: str,
        model: str,
        db_collections: List[str],
        llm_server_hostname: str,
        llm_server_port: int
    ):
        self.persona_id: str = persona_id
        self.name: str = name
        self.description: str = description
        self.db_collections: List[str] = db_collections
        self.collections: List[str] = db_collections
        self.system_prompt: str = system_prompt
        self.model: str = model
        self.llm_server_hostname: str = llm_server_hostname
        self.llm_server_port: int = llm_server_port


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


# I don't think I'm going to use this
def populate_missing_keys_with_none(data, schema):
    """
        Recursively add missing keys from schema with None as the value.
    """
    if isinstance(data, dict) and "properties" in schema:
        for key, sub_schema in schema["properties"].items():
            if key not in data:
                data[key] = None  # Add missing key with None
            else:
                # Recursively apply to nested objects
                data[key] = populate_missing_keys_with_none(
                    data[key],
                    sub_schema
                )

    elif isinstance(data, dict) and "patternProperties" in schema:
        # Handle dynamic keys (like personas)
        pattern_schema = next(iter(schema["patternProperties"].values()))
        for key in data.keys():
            data[key] = populate_missing_keys_with_none(
                data[key],
                pattern_schema
            )

    return data


# CONFIG_SCHEMA = {
#     "type": "object",
#     "properties": {
#         "personas": {
#             "type": "object",
#             "patternProperties": {
#                 ".*": {  # Allows any persona name as a key
#                     "type": "object",
#                     "properties": {
#                         "name": {"type": "string"},
#                         "description": {"type": "string"},
#                         "system_prompt": {"type": "string"},
#                         "model": {"type": "string"},
#                         "temperature": {"type": "number"},
#                         "max_tokens": {"type": "integer"},
#                         "hostname": {"type": "string"},
#                         "port": {"type": "integer"},
#                         "db_collections": {
#                             "type": "array",
#                             "items": {
#                                 "type": "string"
#                             }
#                         },
#                         "formatting": {
#                             "type": "object",
#                             "properties": {
#                                 "user_color": {"type": "string"},
#                                 "persona_color": {"type": "string"},
#                                 "max_line_length": {"type": "integer"},
#                             },
#                             "required": [],
#                             "additionalProperties": False
#                         }
#                     },
#                     "required": [
#                         "name",
#                         "system_prompt",
#                         "model",
#                     ],
#                     "additionalProperties": False
#                 }
#             }
#         },
#         "global_settings": {
#             "type": "object",
#             "properties": {
#                 "user_color": {"type": "string"},
#                 "persona_color": {"type": "string"},
#                 "llm_server": {
#                     "type": "object",
#                     "properties": {
#                         "hostname": {"type": "string"},
#                         "port": {"type": "integer"}
#                     },
#                     "required": [],
#                     "additionalProperties": False,
#                 },
#                 "document_server": {
#                     "type": "object",
#                     "properties": {
#                         "hostname": {"type": "string"},
#                         "port": {"type": "integer"}
#                     },
#                     "required": [],
#                     "additionalProperties": False,
#                 },
#             },
#             "required": [],
#             "additionalProperties": False,
#         },
#     },
#     "required": ["personas"],
#     "additionalProperties": False
# }

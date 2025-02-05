import pathlib
from typing import Optional, List
import sys

from jsonschema import validate, ValidationError
import yaml


class Config:
    def __init__(self, config_path: pathlib.Path):
        config_dict = load_config(config_path)

        # Populate Global Settings
        global_settings_dict = config_dict.get("global_settings", {})

        """
            This seems a little janky. But if the "global_settings" key doesn't
            exist, this will set the global_settings_dict to an empty dict,
            and then it will populate the following values with defaults.
            If it does exist, it will populate the following values with
            the values contained in the dict.

        """
        self.global_user_color = global_settings_dict.get(
            "user_color",
            "green"
        )
        self.global_persona_color = global_settings_dict.get(
            "persona_color",
            "pink"
        )

        # Populate server dict from Global settings
        global_llm_server_dict = global_settings_dict.get(
            "llm_server",
            {}
        )
        self.llm_server_hostname = global_llm_server_dict.get(
            "hostname",
            "localhost"
        )
        self.llm_server_port = global_llm_server_dict.get(
            "port",
            11434
        )

        # Populate server dict from Global settings
        global_document_server_dict = global_settings_dict.get(
            "document_server",
            {}
        )
        self.document_server_hostname = global_document_server_dict.get(
            "hostname",
            "localhost"
        )
        self.document_server_port = global_document_server_dict.get(
            "port",
            11434
        )

        """
            The following is a type of interface for the persona dictionary.
            I'm doing it this way in case I ever want to restructure the yaml
            I can decouple parsing the yaml using instantiations of the config
            class to populate values for personas.

            It also allows me to handle empty values before they get to the
            persona class.

        """
        self.persona_dict = {}
        config_personas = config_dict["personas"]
        for persona_id in config_personas.keys():
            current_persona = config_personas[persona_id]
            name = current_persona.get("name", "default")
            description = current_persona.get(
                "description",
                "A chat bot."
            )
            system_prompt = current_persona.get(
                "system_prompt",
                None
            )
            model = current_persona.get("model", None)
            db_collections = current_persona.get("db_collections", None)

            server = current_persona.get("server", {})
            llm_server_hostname = (
                server.get(
                    "hostname",
                    self.llm_server_hostname)
            )
            llm_server_port = (
                server.get(
                    "port",
                    self.llm_server_port)
            )

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


def load_config(config_path: pathlib.Path) -> dict:
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    try:
        validate(instance=config, schema=CONFIG_SCHEMA)
        # print("✅ Config is valid!")
        return config
    except ValidationError as e:
        print(f"❌ Config validation failed: {e.message}")
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


CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "personas": {
            "type": "object",
            "patternProperties": {
                ".*": {  # Allows any persona name as a key
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "system_prompt": {"type": "string"},
                        "model": {"type": "string"},
                        "temperature": {"type": "number"},
                        "max_tokens": {"type": "integer"},
                        "hostname": {"type": "string"},
                        "port": {"type": "integer"},
                        "db_collections": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "formatting": {
                            "type": "object",
                            "properties": {
                                "user_color": {"type": "string"},
                                "persona_color": {"type": "string"},
                                "max_line_length": {"type": "integer"},
                            },
                            "required": [],
                            "additionalProperties": False
                        }
                    },
                    "required": [
                        "name",
                        "system_prompt",
                        "model",
                    ],
                    "additionalProperties": False
                }
            }
        },
        "global_settings": {
            "type": "object",
            "properties": {
                "user_color": {"type": "string"},
                "persona_color": {"type": "string"},
                "llm_server": {
                    "type": "object",
                    "properties": {
                        "hostname": {"type": "string"},
                        "port": {"type": "integer"}
                    },
                    "required": [],
                    "additionalProperties": False,
                },
                "document_server": {
                    "type": "object",
                    "properties": {
                        "hostname": {"type": "string"},
                        "port": {"type": "integer"}
                    },
                    "required": [],
                    "additionalProperties": False,
                },
            },
            "required": [],
            "additionalProperties": False,
        },
    },
    "required": ["personas"],
    "additionalProperties": False
}

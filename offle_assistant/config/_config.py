import pathlib
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
        global_server_dict = global_settings_dict.get(
            "server",
            {}
        )
        self.global_hostname = global_server_dict.get(
            "hostname",
            "localhost"
        )
        self.global_port = global_server_dict.get(
            "port",
            11434
        )

        """
            The following is a type of interface for the persona dictionary.
            I'm doing it this way in case I ever want to restructure the yaml
            I can decouple parsing the yaml using instantiations of the config
            class to populate values for personas.

            Each entry in the dictionary follows this format:

            "Ralph": {
                "name": ralph,
                "system_prompt": "You are an angry assistant.",
                "model": "llama3.2",
                "rag_dir": None,
                "formatting": {
                    "user_color": "cyan",
                    "persona_color": "pink"
                },
                "server": {
                    "hostname": "localhost",
                    "port": 11434
                }
            }
        """
        self.persona_dict = {}
        config_personas = config_dict["personas"]
        for persona_id in config_personas.keys():
            current_persona = config_personas[persona_id]
            new_persona = {}
            new_persona["name"] = current_persona.get("name", "default")
            new_persona["description"] = current_persona.get(
                "description",
                "A chat bot."
            )
            new_persona["system_prompt"] = current_persona.get(
                "system_prompt",
                None
            )
            new_persona["model"] = current_persona.get("model", None)
            new_persona["rag_dir"] = current_persona.get("rag_dir", None)
            new_persona["formatting"] = current_persona.get("formatting", {})

            """
                This is the same jankiness as the global settings thing where
                If the dict exists, I need to propagate the changes down,
                If it doesn't exist, I need a way of setting default values.
            """
            new_persona["formatting"]["user_color"] = (
                new_persona["formatting"].get(
                    "user_color",
                    self.global_user_color)
            )
            new_persona["formatting"]["persona_color"] = (
                new_persona["formatting"].get(
                    "persona_color",
                    self.global_persona_color
                )
            )

            new_persona["server"] = current_persona.get("server", {})
            new_persona["server"]["hostname"] = (
                new_persona["server"].get(
                    "hostname",
                    self.global_hostname)
            )
            new_persona["server"]["port"] = (
                new_persona["server"].get(
                    "port",
                    self.global_port)
            )

            self.persona_dict[persona_id] = new_persona


def load_config(config_path: pathlib.Path) -> dict:
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    try:
        validate(instance=config, schema=CONFIG_SCHEMA)
        print("✅ Config is valid!")
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
                        "rag_dir": {"type": "string"},
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
                "server": {
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

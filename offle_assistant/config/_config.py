import pathlib
import sys

from jsonschema import validate, ValidationError
import yaml


class Config:
    def __init__(self, config_path: pathlib.Path):
        config_dict = self.load_config(config_path)
        self.global_user_color = config_dict["global_settings"]["user_color"]

    def load_config(self, config_path: pathlib.Path) -> dict:
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


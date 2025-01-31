from jsonschema import validate, ValidationError
import sys
import yaml


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
        "server": {
            "type": "object",
            "properties": {
                "hostname": {"type": "string"},
                "port": {"type": "integer"}
            }
        }
    },
    "required": ["personas"],
    "additionalProperties": False
}


def load_config(config_path):
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
        return None

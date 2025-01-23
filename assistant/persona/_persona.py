import yaml
import pathlib


class Persona:
    def __init__(self, persona_id: str, config_path: pathlib.Path):
        self.persona_id = persona_id
        config = self.load_config(config_path)
        self.name = config["name"]
        self.model = config["model"]
        self.system_prompt = config["system_prompt"]
        self.description = config["description"]

        if config["rag"]["enabled"] is True:
            self.rag = config["rag"]["documents"]
        else:
            self.rag = None

        self.formatting = Formatting(
            formatting_config=config.get("formatting", None)
        )

    def load_config(self, config_path: pathlib.Path):
        with open(config_path, "r") as f:
            config_dict = yaml.safe_load(f)
            persona_config = config_dict["personas"][self.persona_id]
            return persona_config


class Formatting:
    def __init__(self, formatting_config=None):
        if formatting_config is not None:
            default_color = "red"
            self.user_color = formatting_config.get(
                "user_color",
                default_color
            )
            self.persona_color = formatting_config.get(
                "persona_color",
                default_color
            )


def get_persona_strings(config_path: pathlib.Path) -> list[Persona]:
    with open(config_path, "r") as f:
        config_dict = yaml.safe_load(f)

        persona_strings = []
        for persona_id in config_dict["personas"].keys():
            persona = Persona(
                persona_id=persona_id,
                config_path=config_path
            )
            persona_string = "\n".join(
                [
                    persona.name + ":",
                    "\tDescription: " + persona.description,
                    "\tModel: " + persona.model

                ]
            )
            persona_strings.append(persona_string)
        return persona_strings

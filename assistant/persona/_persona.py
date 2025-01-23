import ollama
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import FormattedText
import yaml
import pathlib


class Persona:
    def __init__(self, persona_id: str, config_path: pathlib.Path):
        self.persona_id = persona_id
        config = self.load_config(config_path)
        self.name = config["name"]
        self.model = config["model"]
        self.description = config["description"]
        self.system_prompt = f"Your name is{self.name}" \
            + config["system_prompt"]

        if config["rag"]["enabled"] is True:
            self.rag = config["rag"]["documents"]
        else:
            self.rag = None

        self.formatting = Formatting(
            formatting_config=config.get("formatting", None)
        )

        self.system_prompt_message = {
            "role": "system",
            "content": self.system_prompt
        }

    def load_config(self, config_path: pathlib.Path):
        with open(config_path, "r") as f:
            config_dict = yaml.safe_load(f)
            persona_config = config_dict["personas"][self.persona_id]
            return persona_config

    def chat(self):
        message_chain = []
        while True:

            user_prompt = FormattedText([
                (f"fg:{self.formatting.user_color} bold", "User: ")
            ])
            user_response = prompt(user_prompt)
            user_message = {
                "role": "user",
                "content": "User: " + user_response
            }
            message_chain.append(self.system_prompt_message)
            message_chain.append(user_message)

            if user_response == "\\end":
                break

            chat_response = ollama.chat(
                model=self.model,
                messages=message_chain,
                stream=True,
                # https://github.com/ollama/ollama/blob/main/docs/api.md#generate-request-with-options
                options={"temperature": 0.8}
            )

            print()
            response_text = ""
            ralph_prompt = FormattedText([
                (f"fg:{self.formatting.persona_color} bold", f"{self.name}: ")
            ])
            print(ralph_prompt, end='', flush=True)
            for chunk in chat_response:
                chunk_content = chunk['message']['content']
                print(chunk_content, end='', flush=True)
                response_text += chunk_content

            print()
            print()
            chat_message = {
                "role": "assistant",
                "content": response_text
            }
            message_chain.append(chat_message)


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

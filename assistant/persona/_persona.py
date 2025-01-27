import ollama
import yaml
import pathlib
from typing import Union, Generator

from assistant.formatting import Formatting


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
        self.message_chain = []
        self.temperature = 0.8

    def load_config(self, config_path: pathlib.Path):
        with open(config_path, "r") as f:
            config_dict = yaml.safe_load(f)
            persona_config = config_dict["personas"][self.persona_id]
            return persona_config

    def chat(
        self, user_response, stream: bool = False
    ) -> Union[str, Generator[str, None, None]]:
        while True:

            user_message = {
                "role": "user",
                "content": "User: " + user_response
            }
            self.message_chain.append(self.system_prompt_message)
            self.message_chain.append(user_message)

            if stream is True:
                chat_response = ollama.chat(
                    model=self.model,
                    messages=self.message_chain,
                    stream=True,
                    # https://github.com/ollama/ollama/blob/main/docs/api.md#generate-request-with-options
                    options={"temperature": self.temperature}
                )

                def response_generator():
                    response_text = ""
                    for chunk in chat_response:
                        chunk_content = chunk['message']['content']
                        yield chunk_content
                        response_text += chunk_content

                    chat_message = {
                        "role": "assistant",
                        "content": response_text
                    }
                    self.message_chain.append(chat_message)

                return response_generator()
            else:
                chat_response = ollama.chat(
                    model=self.model,
                    messages=self.message_chain,
                    stream=False,
                    # https://github.com/ollama/ollama/blob/main/docs/api.md#generate-request-with-options
                    options={"temperature": self.temperature}
                )
                response_text = chat_response['message']['content']
                chat_message = {
                    "role": "assistant",
                    "content": response_text
                }
                self.message_chain.append(chat_message)

                return response_text


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

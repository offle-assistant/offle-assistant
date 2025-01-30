import ollama
import pathlib
from typing import Union, Generator
import yaml
import sys

from offle_assistant.formatting import Formatting


class Persona:
    def __init__(
        self,
        persona_id: str,
        config_path: pathlib.Path,
        hostname: str = 'localhost',
        port: int = 11434
    ):
        self.persona_id = persona_id

        # This handles providing a server ip/port
        try:
            server_url = 'http://localhost:11434'
            self.chat_client = ollama.Client(server_url)
        except Exception as e:
            print(f"An exception occurred: {e}")
            sys.exit(1)

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

            chat_response = self.chat_client.chat(
                model=self.model,
                messages=self.message_chain,
                stream=stream,
                # https://github.com/ollama/ollama/blob/main/docs/api.md#generate-request-with-options
                options={
                    "temperature": self.temperature,
                }
            )

            if stream is True:
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

import ollama
from ollama import ChatResponse
import pathlib
from typing import Union, Generator, List, Optional
import yaml
import sys

from qdrant_client.models import PointStruct

from offle_assistant.vector_db import VectorDB
from offle_assistant.vectorizer import Vectorizer


class Persona:
    def __init__(
        self,
        persona_id: str,
        name: str,
        description: str,
        system_prompt: str,
        db_collections: List[str],
        model: str,
        vector_db: Optional[VectorDB] = None,
        llm_server_hostname: str = 'localhost',
        llm_server_port: int = 11434,
    ):
        self.persona_id: str = persona_id
        self.name: str = name
        self.description: str = description
        self.db_collections: List[str] = db_collections
        self.system_prompt: str = f"Your name is {self.name}. " + system_prompt
        self.model: str = model
        self.vector_db = vector_db
        self.llm_server_hostname: str = llm_server_hostname
        self.llm_server_port: int = llm_server_port

        # This handles providing a server ip/port
        try:
            server_url = (
                f'http://{self.llm_server_hostname}:{self.llm_server_port}'
            )
            self.chat_client = ollama.Client(server_url)
        except Exception as e:
            print(f"An exception occurred while connecting to llm server: {e}")
            sys.exit(1)

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
        self,
        user_response,
        stream: bool = False,
        perform_rag: bool = False
    ) -> Union[str, Generator[str, None, None]]:
        rag_prompt = ""
        if perform_rag:
            vectorizer: Vectorizer = self.get_vectorizer(
                self.db_collections[0]
            )
            query_vector = vectorizer.embed_sentence(user_response)
            points: List[PointStruct] = self.vector_db.query_collection(
                collection_name=self.db_collections[0],
                query_vector=query_vector
            )

            docs_string = [point.payload['embedded_text'] for point in points]

            rag_prompt += "Given this context, answer the user's query.\n"
            rag_prompt += (
                f"Context: {docs_string}\n"
            )
            print("\n\nPrompt given to bot: \n", rag_prompt, "\n\n")

        user_message = {
            "role": "user",
            "content": rag_prompt + "User: " + user_response
        }
        self.message_chain.append(self.system_prompt_message)
        self.message_chain.append(user_message)

        chat_response: ChatResponse = self.chat_client.chat(
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

    def get_rag_prompt(
        self,
        user_response: str,
    ) -> str:
        rag_prompt: str = ""
        return rag_prompt

    def get_vectorizer(self, collection_name: str) -> Vectorizer:
        vectorizer: Vectorizer = self.vector_db.get_collection_vectorizer(
            collection_name=collection_name
        )
        return vectorizer


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

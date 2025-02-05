import ollama
from ollama import ChatResponse
import pathlib
from typing import Union, Generator, List, Optional
import yaml
import sys

from offle_assistant.vector_db import (
    VectorDB,
    DbReturnObj,
    EmptyDbReturn
)
from offle_assistant.vectorizer import Vectorizer


class Persona:
    """

    The Persona class handles all chat functionality and has the ability
    to perform RAG before providing an answer.

    In order to perform RAG, you must provide the Persona constructor
    with a vectorDB. It might make sense down the line to be able to
    provide the vectorDB directly to the Persona.chat() method so that
    you can select different DBs to query from mid-conversation.


    """

    def __init__(
        self,
        persona_id: str,
        name: str,
        description: str,
        system_prompt: str,
        db_collections: List[str],
        model: str,
        vector_db: Optional[VectorDB] = None,
        query_threshold: Optional[float] = None,
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
        self.query_threshold: Optional[float] = query_threshold

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

    def get_RAG_prompt(
        self,
        RAG_hit: DbReturnObj = None,
        # rag_template: Optional[] = None,
    ):
        """
        There's probably a better way to do this.
        I will fix this once I have a better idea of how
        the user will be able to customize the rag prompt.

        Probably, what I'll do here is have an object
        called a rag template which will have a bunch of properties
        on it for different aspects of the prompt and then there
        will be a method on it that will return a dictionary
        in a specific format that we can use to fill in fields
        in the prompt.
        """
        if RAG_hit.get_hit_success() is True:
            rag_prompt = (
                "Given the following context, answer the user's query:\n\n"
            )
            rag_prompt += (
                f"Context: {RAG_hit.get_hit_text()}\n"
            )
            return rag_prompt
        else:
            return ""

    def chat(
        self,
        user_response,
        stream: bool = False,
        perform_rag: bool = False
    ) -> Union[str, Generator[str, None, None]]:

        rag_prompt = ""
        rag_response: DbReturnObj = EmptyDbReturn()
        if perform_rag is True:
            if self.vector_db is None:
                print("Cannot perform RAG without a vectorDB.")
            elif len(self.db_collections) <= 0:
                print("Cannot perform RAG without a specified collection.")
            else:
                rag_response: Optional[DbReturnObj] = (
                    self.retrieve_context_doc(
                        query_string=user_response,
                        collection_name=self.db_collections[0]
                    )
                )

                rag_prompt += self.get_RAG_prompt(
                    RAG_hit=rag_response,
                )

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

            persona_chat_response: PersonaChatResponse = PersonaChatResponse(
                chat_response=response_generator(),
                rag_response=rag_response
            )

            return persona_chat_response
        else:
            response_text = chat_response['message']['content']
            chat_message = {
                "role": "assistant",
                "content": response_text
            }
            self.message_chain.append(chat_message)

            persona_chat_response: PersonaChatResponse = PersonaChatResponse(
                chat_response=response_text,
                rag_response=rag_response
            )
            return persona_chat_response

    def retrieve_context_doc(
        self,
        query_string: str,
        collection_name: str
    ) -> DbReturnObj:
        vectorizer: Vectorizer = self.get_vectorizer(
            self.db_collections[0]
        )
        query_vector = vectorizer.embed_sentence(query_string)
        db_return_obj: DbReturnObj = self.vector_db.query_collection(
            collection_name=collection_name,
            query_vector=query_vector,
            score_threshold=self.query_threshold
        )

        return db_return_obj

    def get_vectorizer(self, collection_name: str) -> Vectorizer:
        vectorizer: Vectorizer = self.vector_db.get_collection_vectorizer(
            collection_name=collection_name
        )
        return vectorizer


class PersonaChatResponse:
    def __init__(
        self,
        chat_response: Union[str, Generator[str, None, None]],
        rag_response: DbReturnObj,
    ):
        self.chat_response: Union[str, Generator[str, None, None]] = chat_response
        self.rag_response: DbReturnObj = rag_response


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

import pathlib
import pickle
from typing import Union, Generator, List, Optional
import yaml

from offle_assistant.config import (
    PersonaConfig,
    # RAGConfig,
    StrictBaseModel
)
from offle_assistant.vector_db import (
    VectorDB,
    DbReturnObj,
)
from offle_assistant.vectorizer import Vectorizer
from offle_assistant.llm_client import LLMClient


class PersonaChatResponse(StrictBaseModel):
    chat_response: Union[str, Generator[str, None, None]] = ""
    rag_response: DbReturnObj = DbReturnObj()


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
        config: PersonaConfig
    ):
        self.persona_id: str = persona_id
        self.name: str = config.name
        self.model: str = config.model
        self.description: str = config.description
        self.system_prompt: str = (
            f"Your name is {self.name}. " + config.system_prompt
        )
        self.temperature: float = config.temperature
        self.query_threshold: Optional[float] = config.rag.threshold
        self.db_collections: List[str] = config.rag.collections

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
                f"Context: {RAG_hit.get_hit_document_string()}\n"
            )
            return rag_prompt
        else:
            return ""

    def chat(
        self,
        user_response,
        llm_client: LLMClient,
        vector_db: VectorDB,
        stream: bool = False,
        perform_rag: bool = False,
        api_string: str = "ollama",
        # collection_name: str = ""
    ) -> Union[str, Generator[str, None, None]]:

        rag_prompt = ""
        rag_response: DbReturnObj = DbReturnObj()
        if perform_rag is True:
            if vector_db is None:
                print("Cannot perform RAG without a vectorDB.")
            elif len(self.db_collections) <= 0:
                print("Cannot perform RAG without a specified collection.")
            else:
                rag_response: Optional[DbReturnObj] = (
                    vector_db.query_collection(
                        collection_name=self.db_collections[0],
                        query_string=user_response,
                        score_threshold=self.query_threshold,
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

        chat_response: Union[str, Generator[str, None, None]] = (
            llm_client.chat(
                model=self.model,
                message_chain=self.message_chain,
                stream=stream,
                api_string=api_string
            )
        )

        if stream is True:
            def response_generator():
                response_text = ""
                for chunk in chat_response:
                    chunk_content = chunk
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
            response_text = chat_response
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

    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(serialized_persona):
        return pickle.loads(serialized_persona)

    # def get_config(self):
    #     rag_config: RAGConfig = RAGConfig(
    #         collections=self.db_collections,
    #         threshold=self.query_threshold
    #             )
    #     config: PersonaConfig = PersonaConfig(
    #         name=self.name,
    #         models=self.model,
    #         system_prompt=self.system_prompt,
    #         description=self.description,
    #         temperature=self.temperature,
    #         rag_config=rag_config
    #     )

    #     return config


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

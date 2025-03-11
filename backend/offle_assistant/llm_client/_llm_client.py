import logging
from typing import Union, Generator, List, Dict, Optional
import sys

import ollama
from ollama import ChatResponse
from pydantic import BaseModel

from offle_assistant.config import LLMServerConfig
from offle_assistant.models import (
    LanguageModelsCollection,
    TagInfo,
    ModelDetails
)


class ModelDict(BaseModel):
    Models: Dict[str, List[str]]


class LLMClient:
    def __init__(
        self,
        ollama_server_config: LLMServerConfig,
        language_models: Optional[LanguageModelsCollection] = None
    ):
        ollama_server_url = (
            f'http://{ollama_server_config.hostname}:'
            f'{ollama_server_config.port}'
        )
        self.ollama_client = ollama.Client(ollama_server_url)
        self.language_models = language_models

    def update_models(
        self,
        language_models: LanguageModelsCollection
    ):
        self.language_models = language_models

    async def pull_models(
        self,
    ) -> bool:
        for model_details in self.language_models.models:
            model_details: ModelDetails = model_details
            if model_details.provider == "meta":
                for tag, tag_info in model_details.model_fields.items():
                    tag_info: TagInfo = tag_info
                    model_string = (
                        model_details.name + ":" + tag_info.name
                    )
                    logging.info(f"Pulling model: {model_string}")
                    try:
                        self.ollama_client.pull(model_string)
                    except Exception as e:
                        print(f"Exception encountered: {e}")
                        return False  # failure
        return True  # success

    def chat(
        self,
        model: str,
        api_string: str,
        message_chain: dict,
        stream: bool = False,
    ) -> Union[str, Generator[str, None, None]]:

        client_chat_dict = self.get_client_chat_dict()
        chat_response = client_chat_dict[api_string](
            model=model,
            message_chain=message_chain
        )

        return chat_response

    def ollama_chat(
        self,
        model: str,
        message_chain: dict,
        stream: bool = False,
    ) -> Union[str, Generator[str, None, None]]:

        chat_response: ChatResponse = self.ollama_client.chat(
            model=model,
            messages=message_chain,
            stream=stream,
            # https://github.com/ollama/ollama/blob/main/docs/api.md#generate-request-with-options
            # options={
            #     "temperature": .8,
            # }
        )

        if stream is True:
            def response_generator():
                for chunk in chat_response:
                    chunk_content = chunk['message']['content']
                    yield chunk_content

            return response_generator()

        else:
            response_text = chat_response['message']['content']
            return response_text

    def open_ai_chat(self):
        print("UNIMPLEMENTED")
        sys.exit(1)

    def get_client_chat_dict(self):
        """

        Anytime you add an implementation for a new API, it must match all
        other API function signatures. Or at least be compatible with them.
        Also totally possible to just add the new parameter to the other
        client_chat calls and just silently dispose of it. But write a note
        about what you're doing in a comment.

        """
        return {
            "ollama": self.ollama_chat,
            "open-ai": self.open_ai_chat,
        }

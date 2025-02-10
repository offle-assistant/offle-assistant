from typing import Generator

from prompt_toolkit import print_formatted_text as fprint
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.validation import Validator, ValidationError

from offle_assistant.config import (
    OffleConfig,
    LLMServerConfig,
    VectorDbServerConfig
)
from offle_assistant.persona import (
    Persona,
    PersonaChatResponse
)
from offle_assistant.llm_client import LLMClient
from offle_assistant.vector_db import (
    QdrantDB,
    VectorDB,
    DbReturnObj
)
from offle_assistant.models import PersonaModel


def chat_command(
    args,
    config: OffleConfig
):

    # persona_id is often, but not necessarily, the persona's name.
    persona_id = args.persona
    persona_dict = config.personas
    persona_model: PersonaModel = persona_dict[persona_id]

    qdrant_db: VectorDB = QdrantDB(
        VectorDbServerConfig(
            hostname=config.settings.vector_db_server.hostname,
            port=config.settings.vector_db_server.port
        )
    )

    ollama_server_config: LLMServerConfig = LLMServerConfig(
        hostname=config.settings.llm_server.hostname,
        port=config.settings.llm_server.port,
    )
    llm_client: LLMClient = LLMClient(
        ollama_server_config=ollama_server_config
    )

    persona: Persona = Persona(
        persona_model=persona_model
    )

    while True:
        user_prompt = FormattedText([
            (f"fg:{config.settings.formatting.user_color} bold", "User: ")
        ])
        user_response = prompt(user_prompt, validator=NonEmptyValidator())

        ralph_prompt = FormattedText([
            (
                f"fg:{config.settings.formatting.persona_color} bold",
                f"{persona.name}: "
            )
        ])

        # Check for ending conversation
        conversation_enders = [
            "/end",
            "/bye",
            "/seeya"
        ]

        if user_response in conversation_enders:
            print()
            fprint(ralph_prompt, "Goodbye!\n")
            break

        if args.no_stream is True:
            # Non-streamed version of response
            fprint()
            fprint(ralph_prompt, end='', flush=True)
            chat_response: PersonaChatResponse = persona.chat(
                user_response=user_response,
                stream=False,
                perform_rag=args.rag,
                vector_db=qdrant_db,
                llm_client=llm_client,
            )
            response_text: str = chat_response.chat_response
            fprint(response_text)
            fprint()
        else:
            # Streamed version of response
            fprint()
            chat_response: PersonaChatResponse = persona.chat(
                user_response=user_response,
                stream=True,
                perform_rag=args.rag,
                vector_db=qdrant_db,
                llm_client=llm_client,
            )
            rag_response: DbReturnObj = chat_response.rag_response
            if rag_response.get_hit_success():
                fprint("RAG prompt given to LLM: ")
                fprint("---" * 10)
                fprint(persona.get_RAG_prompt(rag_response))
                fprint("---" * 10)
                fprint("End prompt")
                fprint(
                    f"Distance from query: {rag_response.euclidean_distance}"
                )
                fprint(
                    f"Cosine Similarity: {rag_response.cosine_similarity}"
                )
                fprint(f"Document path: {rag_response.doc_path}")
                fprint("\n")

            fprint(ralph_prompt, end='', flush=True)
            response_stream: Generator[str, None, None] = (
                chat_response.chat_response
            )
            for chunk in response_stream:
                fprint(chunk, end='', flush=True)
            fprint("\n")


class NonEmptyValidator(Validator):
    def validate(self, document):
        if not document.text.strip():  # Strip to handle spaces/newlines
            raise ValidationError(
                message="Please enter a message.",
                cursor_position=0  # Highlight the error at the beginning
            )

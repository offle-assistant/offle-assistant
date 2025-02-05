from typing import Generator

from prompt_toolkit import print_formatted_text as fprint
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.validation import Validator, ValidationError

from offle_assistant.persona import Persona, PersonaChatResponse
from offle_assistant.config import Config, PersonaConfig
from offle_assistant.vector_db import (
    QdrantDB,
    VectorDB,
    DbReturnObj
)


def chat_command(
    args,
    config: Config
):
    qdrant_db: VectorDB = QdrantDB()

    # persona_id is often, but not necessarily, the persona's name.
    persona_id = args.persona
    persona_dict = config.persona_dict
    selected_persona: PersonaConfig = persona_dict[persona_id]
    persona: Persona = Persona(
        persona_id=persona_id,
        name=selected_persona.name,
        description=selected_persona.description,
        db_collections=selected_persona.db_collections,
        vector_db=qdrant_db,
        system_prompt=selected_persona.system_prompt,
        model=selected_persona.model,
        llm_server_hostname=selected_persona.llm_server_hostname,
        llm_server_port=selected_persona.llm_server_port,
    )

    while True:
        user_prompt = FormattedText([
            (f"fg:{config.global_user_color} bold", "User: ")
        ])
        user_response = prompt(user_prompt, validator=NonEmptyValidator())

        ralph_prompt = FormattedText([
            (
                f"fg:{config.global_persona_color} bold",
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
                perform_rag=args.rag
            )
            rag_response: DbReturnObj = chat_response.rag_response
            if rag_response is not None:
                rag_string = rag_response.get_prompt_string()
                fprint("RAG prompt given to LLM: ")
                fprint("---" * 10)
                fprint(rag_string)
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

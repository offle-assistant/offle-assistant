import pathlib

from prompt_toolkit import print_formatted_text as fprint
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.validation import Validator, ValidationError

from offle_assistant.persona import Persona


def chat_command(
    args,
    config_path: pathlib.Path
):
    # persona_id is often, but not necessarily, the persona's name.
    persona_id = args.persona
    persona: Persona = Persona(
        persona_id=persona_id,
        config_path=config_path,
        hostname=args.hostname,
        port=args.port
    )

    while True:

        user_prompt = FormattedText([
            (f"fg:{persona.formatting.user_color} bold", "User: ")
        ])
        user_response = prompt(user_prompt, validator=NonEmptyValidator())

        if user_response == "\\end":
            break

        ralph_prompt = FormattedText([
            (
                f"fg:{persona.formatting.persona_color} bold",
                f"{persona.name}: "
            )
        ])

        if args.no_stream is True:
            # Non-streamed version of response
            fprint()
            fprint(ralph_prompt, end='', flush=True)
            fprint(persona.chat(user_response, stream=False))
            fprint()
        else:
            # Streamed version of response
            fprint()
            fprint(ralph_prompt, end='', flush=True)
            for chunk in persona.chat(user_response, stream=True):
                fprint(chunk, end='', flush=True)
            fprint("\n")


class NonEmptyValidator(Validator):
    def validate(self, document):
        if not document.text.strip():  # Strip to handle spaces/newlines
            raise ValidationError(
                message="Please enter a message.",
                cursor_position=0  # Highlight the error at the beginning
            )

from prompt_toolkit import print_formatted_text as fprint
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.validation import Validator, ValidationError

from offle_assistant.persona import Persona
from offle_assistant.config import Config, PersonaConfig


def chat_command(
    args,
    config: Config
):
    # persona_id is often, but not necessarily, the persona's name.
    persona_id = args.persona
    persona_dict = config.persona_dict
    selected_persona: PersonaConfig = persona_dict[persona_id]
    persona: Persona = Persona(
        persona_id=persona_id,
        name=selected_persona.name,
        description=selected_persona.description,
        system_prompt=selected_persona.system_prompt,
        model=selected_persona.model,
        user_color=selected_persona.user_color,
        persona_color=selected_persona.persona_color,
        hostname=selected_persona.hostname,
        port=selected_persona.port,
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

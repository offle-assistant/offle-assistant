import pathlib
import argparse

from prompt_toolkit import print_formatted_text as fprint
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.validation import Validator, ValidationError

from offle_assistant.persona import get_persona_strings, Persona


# This may need to be handled more elegantly later.
CONFIG_PATH: pathlib.Path = pathlib.Path(
    "~/.config/offle_assistant/config.yaml"
).expanduser()


def main():
    parser = argparse.ArgumentParser(description="CLI Chatbot")
    subparsers = parser.add_subparsers(
        title="subcommand",
        dest="subcommand",
        required=True
    )

    # Subcommand: persona
    parser_persona = subparsers.add_parser(
        "persona",
        help="Subcommand related to managing personas."
    )
    parser_persona.add_argument(
        "--list", "-l",
        action="store_true",
    )
    parser_persona.set_defaults(func=list_personas)

    # Subcommand: chat
    parser_chat = subparsers.add_parser(
        "chat", help="Start a chat with a specified persona"
    )

    parser_chat.add_argument(
        "persona", type=str,
        nargs="?",
        default="default",
        help="Specify the persona name"
    )

    parser_chat.add_argument(
        "--no_stream",
        action="store_true",
        help="Disables text streaming. Response will print to output "
        "after the entire message has been generated."
    )

    parser_chat.add_argument(
        "--hostname", "-n",
        type=str,
        default="localhost",
        help="A hostname or ip address of the server where the "
        "ollama is running from. Default port is 11434. "
        "This can be changed with the '--server_port' option."
    )

    parser_chat.add_argument(
        "--port", "-p",
        type=int,
        default=11434,
        help="The port number that the server is listening on."
        "The default value is 11434."
    )

    parser_chat.set_defaults(func=chat)

    # Parse arguments and call the appropriate function
    args = parser.parse_args()
    args.func(args)


def list_personas(args):  # This is janky, but I'll replace it later.
    persona_strings = get_persona_strings(CONFIG_PATH)
    for string in persona_strings:
        fprint("-----" * 15)
        fprint(string)
        fprint("-----" * 15)


def chat(args):
    # persona_id is often, but not necessarily, the persona's name.
    persona_id = args.persona
    persona: Persona = Persona(
        persona_id=persona_id,
        config_path=CONFIG_PATH,
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


if __name__ == "__main__":
    main()

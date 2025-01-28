import pathlib
import argparse

from prompt_toolkit import print_formatted_text as fprint
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import FormattedText

from offle_assistant.persona import get_persona_strings, Persona


# This may need to be handled more elegantly later.
CONFIG_PATH: pathlib.Path = pathlib.Path(
    "~/.config/offline_assistant.yaml"
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
        "--persona", "-p", type=str,
        help="Specify the persona name"
    )
    parser_chat.add_argument(
        "--no_stream",
        action="store_true",
        help="Disables text streaming. Response will print to output "
        "after the entire message has been generated."
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
    if persona_id is None:  # load default persona if none is provided.
        persona: Persona = Persona(
            persona_id="default",
            config_path=CONFIG_PATH
        )

        while True:

            user_prompt = FormattedText([
                (f"fg:{persona.formatting.user_color} bold", "User: ")
            ])
            user_response = prompt(user_prompt)

            ralph_prompt = FormattedText([
                (
                    f"fg:{persona.formatting.persona_color} bold",
                    f"{persona.name}: "
                )
            ])

            fprint(ralph_prompt, end='', flush=True)
            for chunk in persona.chat(user_response):
                fprint(chunk, end='', flush=True)

    else:  # Load the persona provided.
        persona: Persona = Persona(
            persona_id=persona_id,
            config_path=CONFIG_PATH
        )

        while True:

            user_prompt = FormattedText([
                (f"fg:{persona.formatting.user_color} bold", "User: ")
            ])
            user_response = prompt(user_prompt)

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


if __name__ == "__main__":
    main()

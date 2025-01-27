import pathlib
import argparse

from assistant.persona import get_persona_strings, Persona


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
    parser_chat.set_defaults(func=chat)

    # Parse arguments and call the appropriate function
    args = parser.parse_args()
    args.func(args)


def list_personas(args):  # This is janky, but I'll replace it later.
    persona_strings = get_persona_strings(CONFIG_PATH)
    for string in persona_strings:
        print("-----" * 15)
        print(string)
        print("-----" * 15)


def chat(args):
    # persona_id is often, but not necessarily, the persona's name.
    persona_id = args.persona
    if persona_id is None:  # load default persona if none is provided.
        persona: Persona = Persona(
            persona_id="default",
            config_path=CONFIG_PATH
        )

        persona.chat()

    else:  # Load the persona provided.
        persona: Persona = Persona(
            persona_id=persona_id,
            config_path=CONFIG_PATH
        )

        persona.chat()


if __name__ == "__main__":
    main()

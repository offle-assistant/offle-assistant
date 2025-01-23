import pathlib
import argparse

from assistant.bot import Bot
from assistant.persona import get_persona_strings, Persona


CONFIG_PATH: pathlib.Path = pathlib.Path("./tests/configs/test_config.yaml")


def main():
    parser = argparse.ArgumentParser(description="CLI Chatbot")
    subparsers = parser.add_subparsers(
        title="subcommand",
        dest="subcommand",
        required=True
    )

    parser_list = subparsers.add_parser("list", help="List available personas")
    parser_list.set_defaults(func=list_personas)

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


def list_personas(args):
    persona_strings = get_persona_strings(CONFIG_PATH)
    for string in persona_strings:
        print("-----" * 15)
        print(string)
        print("-----" * 15)


def chat(args):
    persona_id = args.persona
    if persona_id is None:
        persona: Persona = Persona(
            persona_id="default",
            config_path=CONFIG_PATH
        )

        assistant = Bot(persona)
        assistant.chat()
    else:
        persona: Persona = Persona(
            persona_id=persona_id,
            config_path=CONFIG_PATH
        )

        assistant = Bot(persona)
        assistant.chat()


if __name__ == "__main__":
    main()

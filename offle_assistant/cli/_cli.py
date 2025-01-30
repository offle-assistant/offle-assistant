import argparse
import pathlib

from ._chat_command import chat_command
from ._persona_command import persona_command


# This may need to be handled more elegantly later.
CONFIG_PATH: pathlib.Path = pathlib.Path(
    "~/.config/offle_assistant/config.yaml"
).expanduser()


class CLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="CLI Chatbot")
        self.subparsers = self.parser.add_subparsers(
            title="subcommand",
            dest="subcommand",
            required=True
        )
        self.add_persona_parser()
        self.add_chat_parser()

        # Parse arguments
        self.args = self.parser.parse_args()

    def add_persona_parser(self):
        # Subcommand: persona
        parser_persona = self.subparsers.add_parser(
            "persona",
            help="Subcommand related to managing personas."
        )
        parser_persona.add_argument(
            "--list", "-l",
            action="store_true",
        )
        parser_persona.set_defaults(func=persona_command)

    def add_chat_parser(self):
        # Subcommand: chat
        parser_chat = self.subparsers.add_parser(
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

        parser_chat.set_defaults(func=chat_command)

    def run(self):
        # Call the appropriate function
        self.args.func(
            args=self.args,
            config_path=CONFIG_PATH,
        )

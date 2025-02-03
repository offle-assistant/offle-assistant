import argparse
import pathlib
import sys

from ._chat_command import chat_command
from ._persona_command import persona_command
from ._config_command import config_command
from ._rag_command import rag_command

from offle_assistant.config import Config


# This may need to be handled more elegantly later.
SYSTEM_CONFIG: pathlib.Path = pathlib.Path(
    "/etc/offle-assistant/config.yaml"
)
USER_CONFIG: pathlib.Path = pathlib.Path(
    "~/.config/offle-assistant/config.yaml"
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
        self.add_config_parser()
        self.add_rag_parser()

        # Parse arguments
        self.args = self.parser.parse_args()

    def add_config_parser(self):
        # Subcommand: persona
        parser_config = self.subparsers.add_parser(
            "config",
            help="Subcommand related to managing config files."
        )
        parser_config.add_argument(
            "--validate", "-v",
            action="store_true",
        )
        parser_config.set_defaults(func=config_command)

    def add_rag_parser(self):
        # Subcommand: persona
        parser_rag = self.subparsers.add_parser(
            "rag",
            help="Subcommand related to managing RAG documents."
        )

        parser_rag.add_argument(
            "persona", type=str,
            nargs="?",
            default=None,
            help="Specify the persona name"
        )

        parser_rag.add_argument(
            "--add", "-a",
            type=str,
            help="A file or directory to add to the RAG database."
        )

        parser_rag.add_argument(
            "--list", "-l",
            action="store_true",
        )

        parser_rag.set_defaults(func=rag_command)

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
        if USER_CONFIG.is_file():
            print(f"Loading config: {USER_CONFIG}")
            self.config = Config(USER_CONFIG)
        elif SYSTEM_CONFIG.is_file():
            print(f"Loading config: {SYSTEM_CONFIG}")
            self.config = Config(SYSTEM_CONFIG)
        else:
            print("ERROR: no valid config")
            sys.exit(1)

        # Call the appropriate function
        self.args.func(
            args=self.args,
            config=self.config,
        )

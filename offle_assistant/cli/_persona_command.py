from prompt_toolkit import print_formatted_text as fprint

from offle_assistant.persona import get_persona_strings


def persona_command(args, config_path):
    if args.list is True:
        list_personas(config_path=config_path)


def list_personas(config_path):  # This is janky, I'll replace it later.
    persona_strings = get_persona_strings(config_path)
    for string in persona_strings:
        fprint("-----" * 15)
        fprint(string)
        fprint("-----" * 15)

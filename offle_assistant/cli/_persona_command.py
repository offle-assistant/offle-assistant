from prompt_toolkit import print_formatted_text as fprint

from offle_assistant.config import Config


def persona_command(
    args,
    config: Config
):
    if args.list is True:
        list_personas(config=config)


def list_personas(config: Config):  # This is janky, I'll replace it later.
    persona_dict = config.persona_dict
    for persona_id in persona_dict.keys():
        current_persona = persona_dict[persona_id]
        fprint("-----" * 15)
        fprint("Persona ID: ", persona_id)
        fprint("    Persona Name: ", current_persona["name"])
        fprint("    System Prompt: ", current_persona["system_prompt"])
        fprint("    Model: ", current_persona["model"])
        fprint("    Server: ")
        fprint("        hostname: ", current_persona["server"]["hostname"])
        fprint("        port: ", current_persona["server"]["port"])
        fprint("-----" * 15)

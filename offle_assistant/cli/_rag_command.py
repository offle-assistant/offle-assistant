from prompt_toolkit import print_formatted_text as fprint

from offle_assistant.config import Config, PersonaConfig
from offle_assistant.rag import preprocess_docs


def rag_command(
    args,
    config: Config
):
    rag_dir_list = []
    if args.persona is not None:
        persona_id = args.persona
        persona_config: PersonaConfig = config.persona_dict[persona_id]
        rag_dir_list.append(persona_config.rag_dir)
    else:
        for persona_id in config.persona_dict.keys():
            persona_config: PersonaConfig = config.persona_dict[persona_id]
            rag_dir_list.append(persona_config.rag_dir)
    fprint(f"Operating over dirs: {rag_dir_list}")

    for directory in rag_dir_list:
        preprocess_docs(directory)

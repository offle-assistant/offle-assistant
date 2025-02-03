import pathlib

from prompt_toolkit import print_formatted_text as fprint

from offle_assistant.config import Config, PersonaConfig
from offle_assistant.vector_db import QdrantDB


def rag_command(
    args,
    config: Config
):
    if args.add is not None:
        doc_path: pathlib.Path = pathlib.Path(args.add).expanduser()
        qdrant_db = QdrantDB()
        # qdrant_server.clear_db()
        collection_name = "new_db"
        qdrant_db.add_collection(collection_name=collection_name)
        qdrant_db.add_document(
            doc_path=doc_path,
            collection_name=collection_name
        )

        print(
            "client has: "
            f"{qdrant_db.get_db_count(collection_name=collection_name)}"
            " entries."
        )

    # rag_dir_list = []
    # if args.persona is not None:
    #     persona_id = args.persona
    #     persona_config: PersonaConfig = config.persona_dict[persona_id]
    #     rag_dir_list.append(persona_config.rag_dir)
    # else:
    #     for persona_id in config.persona_dict.keys():
    #         persona_config: PersonaConfig = config.persona_dict[persona_id]
    #         rag_dir_list.append(persona_config.rag_dir)
    # fprint(f"Operating over dirs: {rag_dir_list}")

    # for directory in rag_dir_list:
    #     preprocess_docs(directory)

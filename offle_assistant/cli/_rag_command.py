import pathlib

from prompt_toolkit import print_formatted_text as fprint

from offle_assistant.config import OffleConfig, PersonaConfig
from offle_assistant.vector_db import QdrantDB


def rag_command(
    args,
    config: OffleConfig
):
    qdrant_db = QdrantDB()
    if args.add is not None:
        doc_path: pathlib.Path = pathlib.Path(args.add).expanduser()

        collection_name: str = args.collection

        qdrant_db.add_collection(collection_name=collection_name)
        qdrant_db.add_document(
            doc_path=doc_path,
            collection_name=collection_name
        )

        print(
            "client has: "
            f"{qdrant_db.get_entry_count(collection_name=collection_name)}"
            " entries."
        )
    elif args.delete is True:
        collection_name: str = args.collection
        response = qdrant_db.delete_collection(collection_name=collection_name)
        if response is True:
            print(f"Successfully removed collection, {collection_name}")
        else:
            print(f"Could not remove collection, {collection_name}")

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

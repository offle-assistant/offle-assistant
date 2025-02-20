import hashlib
import pathlib
import re
import sys
from typing import Union

import numpy as np
from prompt_toolkit import print_formatted_text as fprint
import pymupdf4llm
from sentence_transformers import SentenceTransformer


def preprocess_docs(
    rag_dir: pathlib.Path,
    overwrite: bool = False
):
    src_dir: pathlib.Path = pathlib.Path(rag_dir, "src/")

    if not src_dir.exists():
        fprint(f"❌ Directory does not exist: {src_dir}")
        sys.exit(1)

    try:
        file_list: list[pathlib.Path] = []
        for file in src_dir.rglob('*'):
            if file.is_file():
                file_list.append(file.resolve())
    except Exception as e:
        print(f"Exception occurred: {e}")

    try:
        processed_files_dir: pathlib.Path = pathlib.Path(
            rag_dir,
            "processed_files/"
        )
        processed_files_dir.mkdir(parents=False, exist_ok=True)
    except Exception as e:
        print(
            f"Exception occurred while creating processed files directory: {e}"
        )
        sys.exit(1)

    """
        If I want to parallelize this, I need to be sure I don't accidentally
        write to the same file twice. Hypothetically, you could have two
        files with the same name but different formats in the src/ dir
        (eg: file_a.pdf and file_a.epub). They would then both be written to
        file_a.md, potentially at the exact same time. Not good.
        Probably, I collect output file names first because that should be
        quick, and then I can perform that check in the loop. If all goes
        well, then we can parallelize safely.
    """
    for file in file_list:
        filename: str = file.stem
        processed_file_path: pathlib.Path = pathlib.Path(
            processed_files_dir,
            filename + ".md"
        )
        if (processed_file_path.exists()) and (overwrite is False):
            fprint(
                f"Skipping {file.name}, file already exists: "
                f"{processed_file_path}"
            )
        else:  # If the file does not exist or if overwrite is True
            md_text: str = pymupdf4llm.to_markdown(file)
            processed_file_path.write_bytes(md_text.encode())


def chunk_and_embed(doc_path: pathlib.Path):
    md_text: str = pymupdf4llm.to_markdown(doc_path)
    paragraphs: list[str] = split_on_lines(markdown_text=md_text)
    embeddings = embed_chunks(chunks=paragraphs)
    return (paragraphs, embeddings)


def embed_chunks(
    chunks: list[str],
    model_string: str = "sentence-transformers/all-mpnet-base-v2"
) -> list[np.array]:
    """
        interface for compute_embeddings.
        This is done so that the inputs/outputs are accurate.
    """
    return compute_embeddings(text=chunks, model_string=model_string)


def embed_sentence(
    sentence: str,
    model_string: str,
) -> np.array:
    """
        interface for compute_embeddings.
        This is done so that the inputs/outputs are accurate.
    """
    return compute_embeddings(text=sentence, model_string=model_string)


def compute_embeddings(
    text: Union[list[str], str],
    model_string: str = "sentence-transformers/all-mpnet-base-v2"
) -> Union[np.array, list[np.array]]:
    """
        This is only intended for use through one of the
        interfaces: embed_chunks or embed_sentence
    """
    model = SentenceTransformer(model_string)
    embeddings = model.encode(text)
    return embeddings


def split_on_lines(markdown_text: str) -> list[str]:
    paragraphs = re.split(r"\n\s*\n+", markdown_text.strip())
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    return paragraphs


def compute_doc_hash(file_path: pathlib.Path) -> str:
    """Compute a SHA-256 hash of the entire file contents."""
    sha = hashlib.sha256()
    with open(file_path, 'rb') as f:
        # Read in chunks to handle large files without using too much memory
        while True:
            data = f.read(65536)  # 64KB chunks
            if not data:
                break
            sha.update(data)
    return sha.hexdigest()

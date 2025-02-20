import pathlib
from typing import Union, List
import sys

import numpy as np
# import pymupdf4llm
from sentence_transformers import SentenceTransformer

from ._vectorizer import Vectorizer
from offle_assistant.text_processing import split_on_lines, latex_to_md


class SentenceTransformerVectorizer(Vectorizer):
    def __init__(
        self,
        model_string: str = "all-mpnet-base-v2",
    ):
        self.model_string = model_string
        self.model_path: str = "sentence-transformers/" + self.model_string
        self.model = SentenceTransformer(self.model_path)

    def embed_chunks(
        self,
        chunks: List[str],
    ) -> List[np.array]:
        """
            interface for compute_embeddings.
            This is done so that the inputs/outputs are accurate.
        """
        return self._compute_embeddings(text=chunks)

    def chunk_and_embed(
        self,
        doc_path: pathlib.Path
    ):
        try:
            md_text: str = latex_to_md(root_dir=doc_path)
        except Exception as e:
            print(f"Exception encountered while chunking and embedding: {e}")
            sys.exit(1)

        if len(md_text) <= 0:  # Catch empty md_text variable
            print(
                f"An error occurred while converting {doc_path} "
                "to a digestible format."
            )
            sys.exit(1)

        paragraphs: List[str] = split_on_lines(text=md_text)

        embeddings = self.embed_chunks(chunks=paragraphs)

        return (paragraphs, embeddings)

    def embed_sentence(
        self,
        sentence: str,
    ) -> np.array:
        """
            interface for compute_embeddings.
            This is done so that the inputs/outputs are accurate.
        """
        return self._compute_embeddings(text=sentence)

    def _compute_embeddings(
        self,
        text: Union[List[str], str],
    ) -> Union[np.array, List[np.array]]:
        """
            This is only intended for use through one of the
            interfaces: embed_chunks or embed_sentence
        """
        try:
            embeddings = self.model.encode(text)
        except Exception as e:
            print(f"Exception encountered while computing embeddings: {e}")
            sys.exit(1)
        return embeddings

    def get_vectorizer_string(self):
        return "sentence-transformer"

    def get_model_string(self):
        return self.model_string

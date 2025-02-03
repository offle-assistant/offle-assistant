import pathlib
import re
from typing import Union, List

import numpy as np
import pymupdf4llm
from sentence_transformers import SentenceTransformer

from ._vectorizer import Vectorizer


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
        md_text: str = pymupdf4llm.to_markdown(doc_path)
        paragraphs: List[str] = self.split_on_lines(markdown_text=md_text)
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
        embeddings = self.model.encode(text)
        return embeddings

    def split_on_lines(
        self,
        markdown_text: str
    ) -> List[str]:
        paragraphs = re.split(r"\n\s*\n+", markdown_text.strip())
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        return paragraphs

    def get_vectorizer_string(self):
        return "sentence-transformer"

    def get_model_string(self):
        return self.model_string

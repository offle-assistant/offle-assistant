from abc import ABC, abstractmethod
import pathlib
from typing import List, Dict, Optional, Type

import numpy as np

from offle_assistant.vectorizer import Vectorizer


class DbReturnObj:
    def __init__(
        self,
        file_name: str,
        doc_path: pathlib.Path,
        document_string: str,
        euclidean_distance: float,
        cosine_similarity: float,
    ):
        self.file_name: str = file_name
        self.doc_path: pathlib.Path = doc_path
        self.document_string: str = document_string
        self.euclidean_distance: float = euclidean_distance
        self.cosine_similarity: float = cosine_similarity

    def get_prompt_string(self) -> str:
        rag_prompt = ""

        rag_prompt += (
            "Given the following context, answer the user's query:\n\n"
        )
        rag_prompt += (
            f"Context: {self.document_string}"
        )
        return rag_prompt


class VectorDB(ABC):
    @abstractmethod
    def add_collection(
        self,
        collection_name: str,
        vectorizer_class: Type[Vectorizer],
        model_string: Optional[str] = None
    ):
        pass

    @abstractmethod
    def delete_collection(
        self,
        collection_name: str
    ):
        pass

    @abstractmethod
    def add_document(
        self,
        doc_path: pathlib.Path,
        collection_name: str,
    ):
        pass

    @abstractmethod
    def get_collection_vectorizer(
        self,
        collection_name: str
    ) -> Vectorizer:
        pass

    @abstractmethod
    def query_collection(
        self,
        collection_name: str,
        query_vector: np.array
    ) -> str:
        pass

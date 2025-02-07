from abc import ABC, abstractmethod
import pathlib
from typing import Optional, Type, List

from offle_assistant.vectorizer import Vectorizer
from offle_assistant.config import StrictBaseModel


class DbReturnObj(StrictBaseModel):
    file_name: str = ""
    doc_path: pathlib.Path = pathlib.Path("")
    document_string: str = ""
    euclidean_distance: float = 0
    cosine_similarity: float = 0
    success: bool = False

    def get_hit_document_string(self):
        return self.document_string

    def get_hit_success(self):
        return self.success


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
        query_string: List[str],
        score_threshold: Optional[float]
    ) -> str:
        pass

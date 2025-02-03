from abc import ABC, abstractmethod
import pathlib
from typing import List, Dict, Optional, Type

from offle_assistant.vectorizer import Vectorizer


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
    def remove_collection(
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

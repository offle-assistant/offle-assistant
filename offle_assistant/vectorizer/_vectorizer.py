from abc import ABC, abstractmethod
from typing import List, Dict, Optional

import numpy as np


class Vectorizer(ABC):
    def __init__(
        self,
        model_string: str
    ):
        pass

    @abstractmethod
    def embed_chunks(
        self,
        chunks: List[str]
    ) -> List[np.array]:
        """
            interface for compute_embeddings.
            This is done so that the inputs/outputs are accurate.
        """
        pass

    @abstractmethod
    def get_vectorizer_string(self) -> str:
        """
            A given db stores which vectorizer was used for embedding its
            documents. The return from this method is used in conjunction
            with the vectorizer_lookup_table to keep track of which
            vectorizer was used for each db and to instantiate the correct
            one at runtime.
        """
        pass

    @abstractmethod
    def get_model_string(self):
        """
            A given db stores which model was used for embedding its
            documents. The return from this method is used to keep track of
            which model was used for each db and to instantiate an instance
            of Vectorizer with the correct one at runtime.
        """
        pass

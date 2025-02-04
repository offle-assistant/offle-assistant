import hashlib
import pathlib
from typing import Optional, Type, List
import sys

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    SearchParams
)
from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue,
)

from offle_assistant.vectorizer import (
    Vectorizer,
    SentenceTransformerVectorizer,
    vectorizer_lookup_table
)
from ._vector_db import VectorDB


class QdrantDB(VectorDB):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
    ):
        self.client: QdrantClient = QdrantClient(host=host, port=port)
        self.metadata_id = 0

    def add_collection(
        self,
        collection_name: str,
        vectorizer_class: Type[Vectorizer] = SentenceTransformerVectorizer,
        model_string: Optional[str] = None
    ):
        existing_collections = self.client.get_collections().collections
        if collection_name not in [
            col.name for col in existing_collections
        ]:
            vectorizer: Vectorizer = (
                vectorizer_class() if model_string is None else
                vectorizer_class(model_string=model_string)
            )
            print(
                f"Collection '{collection_name}' "
                "does not exist. Creating..."
            )

            size_test: str = "this sentence is intended for size detection."
            vectorized_sentence: np.array = vectorizer.embed_sentence(
                sentence=size_test
            )

            # Diff embeddings have diff dims.
            vector_dim: int = vectorized_sentence.shape[0]

            self.client.recreate_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_dim, distance=Distance.COSINE
                ),
            )

            model_metadata = PointStruct(
                id=self.metadata_id,
                vector=[0.0] * vector_dim,  # Dummy vector
                payload={
                    "type": "metadata",
                    "vectorizer": vectorizer.get_vectorizer_string(),
                    "model": vectorizer.get_model_string(),
                    "notes": "Initial embedding model for this collection"
                }
            )

            self.client.upsert(
                collection_name=collection_name,
                points=[model_metadata],
            )
        else:
            print("Collection exists.")

    def query_collection(
        self,
        collection_name: str,
        query_vector: np.array,
    ) -> List[PointStruct]:
        search_params = SearchParams(hnsw_ef=512)
        search_results = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=1,
            search_params=search_params
        )

        return search_results

    def delete_collection(
        self,
        collection_name: str
    ):
        """
        This removes a collection entirely.
        """
        return self.client.delete_collection(collection_name=collection_name)

    def add_document(
        self,
        doc_path: pathlib.Path,
        collection_name: str,
    ):
        doc_path = doc_path.expanduser()
        doc_hash: str = self.compute_doc_hash(doc_path)  # hash of doc content

        print(
            f"\nChecking if document, {doc_path.name}, is in database."
        )

        existing_doc_path: pathlib.Path = self.search_collection_by_doc_id(
            doc_id=doc_hash,
            collection_name=collection_name
        )
        if existing_doc_path:  # Is document already in db.
            print(
                f"\tSkipping document... {doc_path.name} "
                "already exists in database.\n"
                f"\tSource file located at: {existing_doc_path}\n"
            )
        else:  # if not, add it
            vectorizer: Vectorizer = self.get_collection_vectorizer(
                collection_name=collection_name
            )

            next_id: int = self.get_entry_count(
                collection_name=collection_name
            )  # figure out next idx in collection

            points: list[PointStruct] = self.get_document_points(
                doc_id=doc_hash,
                doc_path=doc_path,
                next_id=next_id,
                subset_id="all",
                vectorizer=vectorizer
            )

            self.client.upsert(
                collection_name=collection_name,
                points=points,
            )

    def get_document_points(
        self,
        doc_id: str,
        doc_path: pathlib.Path,
        next_id: int,
        vectorizer,
        subset_id: str = "all",
    ) -> list[PointStruct]:
        paragraphs, embeddings = vectorizer.chunk_and_embed(doc_path=doc_path)

        points: list[PointStruct] = []
        idx: int = 0
        for embedding, paragraph in zip(embeddings, paragraphs):
            new_point: PointStruct = PointStruct(
                id=next_id,
                vector=embedding,
                payload={
                    "doc_id": doc_id,
                    "chunk_id": idx,
                    "file_name": doc_path.name,
                    "doc_path": str(doc_path),
                    "embedded_text": paragraph,
                    "subset_id": subset_id,
                }
            )
            points.append(new_point)
            idx += 1
            next_id += 1

        return points

    def search_collection_by_doc_id(
        self,
        doc_id: str,
        collection_name: str
    ) -> Optional[pathlib.Path]:
        """
        This function takes a doc_hash and checks if any other documents in the
        collection have the same doc_id.

        It would be nice to have this function return the path to the file if
        it returns True.

            def search_collection(doc_id: str) -> Optional[pathlib.Path]:
                if hit:
                    return hit.path
                else:
                    return None

        """
        filter_condition = Filter(
            must=[
                FieldCondition(
                    key="doc_id",                 # Payload key
                    match=MatchValue(value=doc_id)  # The value to match
                )
            ]
        )
        points, _ = self.client.scroll(
            collection_name=collection_name,
            scroll_filter=filter_condition
        )
        if points:
            doc_path: pathlib.Path = pathlib.Path(
                points[0].payload["doc_path"]
            )
            return doc_path
        else:
            return None

    def get_entry_count(self, collection_name):
        return self.client.count(collection_name=collection_name).count

    def get_collection_vectorizer(
        self,
        collection_name: str
    ) -> Vectorizer:
        try:
            result = self.client.retrieve(
                collection_name=collection_name,
                ids=[0]
            )
            if result:
                metadata = result[0].payload
                vectorizer_class: Type[Vectorizer] = vectorizer_lookup_table[
                    metadata["vectorizer"]
                ]
                vectorizer = vectorizer_class(model_string=metadata["model"])
                return vectorizer
            else:
                print(
                    "Cannot determine Vectorizer to use for embeddings. "
                    "No metadata entry in database."
                )
                sys.exit(1)

        except Exception as e:
            print(f"Exception encountered: {e}")
            sys.exit(1)

    def compute_doc_hash(self, file_path: pathlib.Path) -> str:
        """Compute a SHA-256 hash of the entire file contents."""

        try:
            sha = hashlib.sha256()
            with open(file_path, 'rb') as f:
                chunk_size: int = 65536  # 64KB chunks
                # Read in chunks, handles large files w/out using too much mem
                while True:
                    data = f.read(chunk_size)
                    if not data:
                        break
                    sha.update(data)
            return sha.hexdigest()
        except Exception as e:
            print(f"Exception encountered: {e}")
            sys.exit(1)

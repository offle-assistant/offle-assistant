import hashlib
import pathlib
from typing import Optional

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.models import Filter, FieldCondition, MatchValue

from offle_assistant.vectorizer import (
    SentenceTransformerVectorizer,
    vectorizer_table
)


class QdrantDB:
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
        vectorizer_class=SentenceTransformerVectorizer,
        model_string: Optional[str] = None
    ):
        existing_collections = self.client.get_collections().collections
        if collection_name not in [
            col.name for col in existing_collections
        ]:
            vectorizer = (
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

    def remove_collection(
        self,
        collection_name
    ):
        self.client.delete_collection(collection_name=collection_name)

    def clear_collection(
        self,
        collection_name: str
    ):
        self.remove_collection(collection_name=collection_name)

    def add_document(
        self,
        doc_path: pathlib.Path,
        collection_name: str,
    ):
        doc_path = doc_path.expanduser()
        doc_hash: str = self.compute_doc_hash(doc_path)  # hash of doc content

        print(
            f"checking if document, {doc_path.name} is in database."
        )
        if self.is_doc_in_db(
            doc_hash=doc_hash,
            collection_name=collection_name
        ):  # Is document already in db.
            print(
                f"Skipping document... {doc_path.name} "
                "already exists in database."
            )
        else:  # if not, add it
            print("Adding doc to db.")
            result = self.client.retrieve(
                collection_name=collection_name,
                ids=[0]
            )
            if result:
                metadata = result[0].payload
                vectorizer_class = vectorizer_table[metadata["vectorizer"]]
                vectorizer = vectorizer_class(model_string=metadata["model"])
                next_id: int = self.get_db_count(
                    collection_name=collection_name
                )  # figure out next idx
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

            else:
                print(
                    "database has no metadata. "
                    "Can't tell which Vectorizer to use."
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

    def is_doc_in_db(
        self,
        doc_hash: str,
        collection_name: str
    ) -> bool:
        """
        This function takes a doc_id and checks if any other documents in the
        collection have the same doc_id.
        """
        count_result = self.client.count(
            collection_name=collection_name,
            count_filter=Filter(
                must=[
                    FieldCondition(
                        key="doc_id", match=MatchValue(
                            value=doc_hash
                        )
                    )
                ]
            ),
        )
        if count_result.count > 0:
            return True
        else:
            return False

    def get_db_count(self, collection_name):
        return self.client.count(collection_name=collection_name).count

    def compute_doc_hash(self, file_path: pathlib.Path) -> str:
        """Compute a SHA-256 hash of the entire file contents."""
        sha = hashlib.sha256()
        with open(file_path, 'rb') as f:
            chunk_size: int = 65536  # 64KB chunks
            # Read in chunks. handles large files without using too much memory
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                sha.update(data)
        return sha.hexdigest()

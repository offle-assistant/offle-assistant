import pathlib
import sys

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.models import Filter, FieldCondition, MatchValue

from offle_assistant.rag import (
    chunk_and_embed,
    compute_doc_hash,
    embed_sentence
)


class QdrantDB:
    def __init__(
        self,
        collection_name,
        host: str = "localhost",
        port: int = 6333,
        embedding_model: str = None,
        # vectorizer: Vectorizer = None
    ):
        self.client: QdrantClient = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self.metadata_id = 0
        self.embedding_model = embedding_model
        existing_collections = self.client.get_collections().collections

        if self.collection_name not in [
            col.name for col in existing_collections
        ]:
            print(
                f"Collection '{self.collection_name}' "
                "does not exist. Creating..."
            )

            # This is here to make sure that we don't mix models up
            # It is janky right now.
            if self.embedding_model is None:
                self.embedding_model = "sentence-transformers/all-mpnet-base-v2"

            size_test: str = "this sentence is intended for size detection."
            vectorized_sentence: np.array = embed_sentence(
                sentence=size_test,
                model_string=self.embedding_model
            )

            vector_dim: int = vectorized_sentence.shape[0]

            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_dim, distance=Distance.COSINE
                ),
            )

            model_metadata = PointStruct(
                id=self.metadata_id,
                vector=[0.0] * vector_dim,  # Dummy vector
                payload={
                    "type": "metadata",
                    "embedding_model": embedding_model,
                    "notes": "Initial embedding model for this collection"
                }
            )
            self.client.upsert(
                collection_name=self.collection_name,
                points=[model_metadata],
            )
        else:
            print("Collection exists.")
            result = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[0]
            )
            if result:
                metadata = result[0].payload
                db_embedding_model: str = metadata["embedding_model"]
                if (
                    embedding_model is not None
                ) and (
                    embedding_model != db_embedding_model
                ):
                    print(
                        f"Specified embedding model, {embedding_model}, "
                        "does not match database embedding model, "
                        f"{db_embedding_model}"
                    )
                    sys.exit(1)

    def remove_collection(
        self,
        collection_name
    ):
        self.client.delete_collection(collection_name=collection_name)

    def clear_db(self):
        self.remove_collection(collection_name=self.collection_name)

    def add_document(
        self,
        doc_path: pathlib.Path
    ):
        doc_path = doc_path.expanduser()
        doc_id: str = compute_doc_hash(doc_path)  # hash of doc content

        print(
            f"checking if document, {doc_path.name} is in database."
        )
        if self.doc_id_check(doc_id):  # Is document already in db.
            print(
                f"Skipping document... {doc_path.name} "
                "already exists in database."
            )
        else:  # if not, add it
            next_id: int = self.get_db_count()  # figure out what next idx is
            points: list[PointStruct] = self.get_document_points(
                doc_id=doc_id,
                doc_path=doc_path,
                next_id=next_id,
                subset_id="all"
            )
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )

    def get_document_points(
        self,
        doc_id: str,
        doc_path: pathlib.Path,
        next_id: int,
        subset_id: str = "all"
    ) -> list[PointStruct]:
        paragraphs, embeddings = chunk_and_embed(doc_path=doc_path)

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

    def doc_id_check(self, doc_id: str):
        """
        This function takes a doc_id and checks if any other documents in the
        collection have the same doc_id.
        """
        count_result = self.client.count(
            collection_name=self.collection_name,
            count_filter=Filter(
                must=[
                    FieldCondition(
                        key="doc_id", match=MatchValue(
                            value=doc_id
                        )
                    )
                ]
            ),
        )
        if count_result.count > 0:
            return True
        else:
            return False

    def get_db_count(self):
        return self.client.count(collection_name=self.collection_name).count


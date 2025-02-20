from typing import List, Optional, Dict, Literal

from pydantic import BaseModel, Field


QueryMetric = Literal[
    "cosine_similarity",
    "euclidean_distance"
]


class RAGConfig(BaseModel):
    """Configuration for Retrieval-Augmented Generation (RAG)."""

    db_collections: List[str] = Field(
        ...,
        min_items=1,
        description="List of database collections for retrieval"
    )
    query_threshold: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Similarity threshold for document retrieval"
    )
    query_metric: QueryMetric = Field(
        ...,
        description="Distance metric for retrieval (cosine, euclidean, etc)"
    )
    additional_settings: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="Optional extra settings for different vector databases"
    )

    class Config:
        from_attributes = True

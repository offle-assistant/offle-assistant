from typing import List, Optional

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    field_serializer
)
from bson import ObjectId

from ._common_utils import PyObjectId


class TagInfo(BaseModel):
    """Represents tag details for a model."""
    name: str
    hash: str
    size: str


class ModelDetails(BaseModel):
    """
        Represents details about an AI model.
    """

    model_config = {"from_attributes": True}
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    provider: str
    api: str
    tags: List[TagInfo]

    @field_validator("id", mode="before")
    @classmethod
    def parse_id(cls, value):
        if isinstance(value, PyObjectId):
            return str(value)  # or raise ValueError if invalid
        elif isinstance(value, ObjectId):
            return str(value)  # or raise ValueError if invalid
        return value

    @field_serializer("id")
    def serialize_id(self, value: Optional[PyObjectId]) -> Optional[str]:
        # Convert the ObjectId to its string representation if it's not None.
        return None if value is None else str(value)


class LanguageModelsCollection(BaseModel):
    """
        Top-level model that holds multiple models.

        {
            "models": [
                {
                    "name": "llama3.2",
                    "provider": "meta",
                    "api": "ollama",
                    "tags": [
                        {
                            "name": "latest",
                            "hash": "asklfjha",
                            "size": "2 GB",
                        }
                    ]
                },
                {
                    "name": "llama3.2",
                    "provider": "meta",
                    "api": "ollama",
                    "tags": [
                        {
                            "name": "latest",
                            "hash": "asklfjha",
                            "size": "2 GB",
                        }
                    ]
                },
            ]
        }

    """
    models: List[ModelDetails]

from typing import List

from pydantic import BaseModel


class TagInfo(BaseModel):
    """Represents tag details for a model."""
    name: str
    hash: str
    size: str


class ModelDetails(BaseModel):
    """Represents details about an AI model."""
    name: str
    provider: str
    api: str
    tags: List[TagInfo]


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

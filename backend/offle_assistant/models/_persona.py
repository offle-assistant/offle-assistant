from typing import Optional
from datetime import datetime, timezone

from pydantic import (
    Field,
    BaseModel,
    field_serializer,
    field_validator
)

from ._rag import RAGConfig
from ._common_utils import PyObjectId


class PersonaModel(BaseModel):
    model_config = {"from_attributes": True}
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: Optional[PyObjectId] = None
    creator_id: Optional[PyObjectId] = None
    name: str = Field(..., min_length=3, max_length=50)
    description: str = Field(..., max_length=500)
    system_prompt: str = Field(default="You are a helpful AI assistant.")
    model: str = Field(default="llama3.2")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    rag: Optional[RAGConfig] = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @field_serializer("created_at")
    def serialize_timestamp(self, value: datetime | str) -> str:
        # If the value is a string, convert it to a datetime first.
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError:
                # return the value as-is
                return value

        return value.isoformat()

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_timestamp(cls, value):
        # Check for numeric timestamp
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value, tz=timezone.utc)

        # If value is already a string in ISO format, let Pydantic handle it
        return value


class PersonaUpdateModel(BaseModel):
    """Model for updating a Persona."""

    model_config = {"from_attributes": True}
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    system_prompt: Optional[str] = Field(None)
    model: Optional[str] = Field(None)
    temperature: Optional[float] = Field(None, ge=0.0, le=1.0)
    rag: Optional[RAGConfig] = None
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @field_serializer("updated_at")
    def serialize_timestamp(self, value: datetime | str) -> str:
        # If the value is a string, convert it to a datetime first.
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError:
                # return the value as-is
                return value

        return value.isoformat()

    @field_validator("updated_at", mode="before")
    @classmethod
    def parse_timestamp(cls, value):
        # Check for numeric timestamp
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value, tz=timezone.utc)

        # If value is already a string in ISO format, let Pydantic handle it
        return value

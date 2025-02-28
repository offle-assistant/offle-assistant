from typing import List, Optional
from datetime import datetime, timezone

from pydantic import (
    BaseModel,
    Field,
    field_serializer,
    field_validator
)
from bson.objectid import ObjectId

# from ._common_utils import PyObjectId


class MessageContent(BaseModel):
    role: str  # Either "user" or "assistant"
    content: str
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class MessageHistoryModel(BaseModel):
    model_config = {"from_attributes": True}
    id: Optional[str] = Field(alias="_id", default=None)  # MongoDB _id
    title: str = Field(default="Default title", min_length=3, max_length=50)
    description: str = Field(
        default="Default Description",
        min_length=3,
        max_length=50
    )
    messages: List[MessageContent] = []  # List of message objects
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


class MessageHistoryUpdateModel(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = Field(None, min_length=3, max_length=50)
    messages: Optional[List[MessageContent]] = None  # List of message objects

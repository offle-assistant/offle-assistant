from datetime import datetime, timezone
from typing import Optional, List

from pydantic import (
    Field,
    BaseModel,
    field_serializer,
    field_validator
)

from ._common_utils import PyObjectId


class FileMetadata(BaseModel):
    filename: str
    uploaded_by: PyObjectId
    content_type: Optional[str] = Field(default="application/octet-stream")
    description: str = Field(
        default="Default Description",
        min_length=3,
        max_length=50
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    tags: list[str] = []
    groups: List[str] = []

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_timestamp(cls, value):
        # Check for numeric timestamp
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value, tz=timezone.utc)

        # If value is already a string in ISO format, let Pydantic handle it
        return value

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

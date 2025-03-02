from typing import Optional

from bson import ObjectId

from pydantic import (
    Field,
    BaseModel,
    field_serializer,
    field_validator
)

from ._common_utils import PyObjectId


class GroupModel(BaseModel):
    model_config = {"from_attributes": True}
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(..., min_length=3, max_length=50)
    description: str = Field(..., max_length=500)

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


class GroupUpdateModel(BaseModel):
    model_config = {"from_attributes": True}
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=500)

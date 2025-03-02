from datetime import datetime, timezone
from typing import List, Optional, Literal, Dict

from bson import ObjectId
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    RootModel,
    field_serializer,
    field_validator
)

from ._common_utils import PyObjectId


Role = Literal["user", "admin", "builder"]


class PersonaMessageHistoryMap(RootModel[Dict[PyObjectId, List[PyObjectId]]]):
    pass


class UserModel(BaseModel):
    model_config = {"from_attributes": True}
    id: Optional[PyObjectId] = Field(alias="_id", default=None)  # MongoDB _id
    username: str = Field(..., min_length=3, max_length=50)
    role: Role = Field(default="user")
    email: EmailStr
    groups: List[str] = []
    hashed_password: str
    personas: List[PyObjectId] = []
    persona_message_history: PersonaMessageHistoryMap = Field(
        default_factory=lambda: PersonaMessageHistoryMap(root={})
    )
    # If no "created_at" is provided, it's a new user. use the current utc time
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

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

    @field_validator("personas", mode="before")
    @classmethod
    def parse_objectid_list(cls, value):
        """Convert list of strings to list of ObjectIds."""
        if isinstance(value, list):
            return [
                str(v) if ObjectId.is_valid(v) else v for v in value
            ]
        return value

    @field_serializer("personas")
    def serialize_objectid_list(self, value: List[PyObjectId]) -> List[str]:
        """Convert list of ObjectIds to list of strings for JSON output."""
        return [str(v) for v in value]

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


class UserUpdateModel(BaseModel):
    model_config = {"from_attributes": True}
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    role: Optional[Role] = Field(default=None)
    email: Optional[EmailStr] = None
    groups: Optional[List[PyObjectId]] = None
    hashed_password: Optional[str] = None
    personas: Optional[List[PyObjectId]] = None
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @field_validator("updated_at", mode="before")
    @classmethod
    def parse_timestamp(cls, value):
        # Check for numeric timestamp
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value, tz=timezone.utc)

        # If value is already a string in ISO format, let Pydantic handle it
        return value

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

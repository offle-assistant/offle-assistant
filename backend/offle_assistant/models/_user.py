from datetime import datetime
from typing import List, Optional, Literal

from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field

from ._common_utils import PyObjectId


Role = Literal["user", "admin", "builder"]


class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)  # MongoDB _id
    username: str = Field(..., min_length=3, max_length=50)
    role: Role = Field(default="user")
    email: EmailStr
    hashed_password: str
    personas: List[PyObjectId] = []
    # If no "created_at" is provided, it's a new user. use the current utc time
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
        json_encoders = {ObjectId: str}

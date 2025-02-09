from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field

from ._common_utils import PyObjectId


class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)  # MongoDB _id
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    hashed_password: str
    personas: List[PyObjectId] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
        json_encoders = {ObjectId: str}

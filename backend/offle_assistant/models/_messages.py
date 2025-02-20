from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, Field
from bson.objectid import ObjectId

from ._common_utils import PyObjectId


class MessageContent(BaseModel):
    role: str  # Either "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MessageHistoryModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)  # MongoDB _id
    user_id: PyObjectId  # User reference
    persona_id: PyObjectId  # Persona reference
    messages: List[MessageContent] = []  # List of message objects
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
        json_encoders = {ObjectId: str}

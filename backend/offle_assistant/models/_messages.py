from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, Field
from bson.objectid import ObjectId

# from ._common_utils import PyObjectId


class MessageContent(BaseModel):
    role: str  # Either "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MessageHistoryModel(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)  # MongoDB _id
    title: str = Field(default="Default title", min_length=3, max_length=50)
    description: str = Field(
        default="Default Description",
        min_length=3,
        max_length=50
    )
    messages: List[MessageContent] = []  # List of message objects
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
        json_encoders = {ObjectId: str}


class MessageHistoryUpdateModel(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = Field(None, min_length=3, max_length=50)
    messages: Optional[List[MessageContent]] = None  # List of message objects

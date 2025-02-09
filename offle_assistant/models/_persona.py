from typing import Optional
from datetime import datetime

from pydantic import Field, BaseModel

from ._rag import RAGConfig
from ._common_utils import PyObjectId


class PersonaModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: PyObjectId
    name: str = Field(..., min_length=3, max_length=50)
    description: str = Field(..., max_length=500)
    system_prompt: str = Field(default="You are a helpful AI assistant.")
    model: str = Field(default="llama3.2")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    rag: Optional[RAGConfig] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True

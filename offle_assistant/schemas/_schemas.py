from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from offle_assistant.models import PersonaModel

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserOut(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: EmailStr

    model_config = {
        "from_attributes": True,
    }


class PersonaCreateDefault(BaseModel):
    user_id: int
    persona_name: Optional[str] = "Offie"


PersonaOut = PersonaModel
PersonaUpdate = PersonaModel

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRegistration(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=8, max_length=100)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_one_identifier

    @classmethod
    def validate_one_identifier(cls, values):
        if not values.get("username") and not values.get("email"):
            raise ValueError("Either 'username' or 'email' must be provided.")
        return values

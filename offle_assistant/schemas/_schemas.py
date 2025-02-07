from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None


class UserOut(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: EmailStr

    model_config = {
        "from_attributes": True,
    }

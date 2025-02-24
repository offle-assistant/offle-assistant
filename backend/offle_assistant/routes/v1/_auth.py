from datetime import timedelta

# from bson import ObjectId
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from offle_assistant.mongo import users_collection
from offle_assistant.models import UserModel, Role
from offle_assistant.auth import (
    hash_password,
    verify_password,
    create_access_token
)
from offle_assistant.database import create_user_in_db, get_user_by_email

auth_router = APIRouter()


class AuthModel(BaseModel):
    email: str
    password: str


@auth_router.post("/register")
async def register_user(user: AuthModel, role: Role = "user"):
    """Registers a new user with hashed password."""
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:  # Checks if a user exists by email
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create a new user.
    hashed_password = hash_password(user.password)
    new_user = UserModel(
        email=user.email,
        hashed_password=hashed_password,
        username=user.email.split("@")[0],
        role=role
    )

    # Plug the user into the database
    inserted_id = await create_user_in_db(new_user)

    # return a success message with the newly created id
    return {
        "message": "User registered",
        "user_id": str(inserted_id)
    }


@auth_router.post("/login")
async def login_user(user: AuthModel):
    """Authenticates a user and returns a JWT token."""

    # Find user by email
    db_user = await get_user_by_email(user.email)

    # Check if the user query returned a hit and verify password
    if not db_user or not verify_password(
        user.password, db_user["hashed_password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Authentication was successful so create an access token
    access_token = create_access_token(
        {"user_id": str(db_user["_id"])}, expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}

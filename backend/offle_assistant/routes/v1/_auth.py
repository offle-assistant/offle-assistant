from datetime import timedelta

# from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase

from offle_assistant.models import UserModel, GroupModel
from offle_assistant.auth import (
    hash_password,
    verify_password,
    create_access_token
)
from offle_assistant.database import (
    create_user_in_db,
    get_user_by_email,
    get_default_group
)
from offle_assistant.dependencies import get_db

auth_router = APIRouter()


class AuthModel(BaseModel):
    email: str
    password: str


@auth_router.post("/register")
async def register_user(
    user: AuthModel,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Registers a new user with hashed password."""
    existing_user = await get_user_by_email(
        user_email=user.email,
        db=db
    )
    if existing_user:  # Checks if a user exists by email
        raise HTTPException(status_code=400, detail="Email already registered")

    default_group_dict = await get_default_group(db)
    default_group: GroupModel = GroupModel(**default_group_dict)

    default_group_name = default_group.name

    # Create a new user.
    hashed_password = hash_password(user.password)
    new_user = UserModel(
        email=user.email,
        hashed_password=hashed_password,
        username=user.email.split("@")[0],
        groups=[default_group_name],
        role="user"
    )

    # Plug the user into the database
    inserted_id = await create_user_in_db(
        new_user=new_user,
        db=db
    )

    # return a success message with the newly created id
    return {
        "message": "User registered",
        "user_id": str(inserted_id)
    }


@auth_router.post("/login")
async def login_user(
    user: AuthModel,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Authenticates a user and returns a JWT token."""

    # Find user by email
    db_user = await get_user_by_email(
        user_email=user.email,
        db=db
    )

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
        {"user_id": str(db_user["_id"]), "role": db_user["role"]},
        expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}

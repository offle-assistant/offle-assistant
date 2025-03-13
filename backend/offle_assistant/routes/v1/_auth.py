from datetime import timedelta

# from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from offle_assistant.models import (
    UserModel,
    GroupModel,
    UserLogin,
    UserRegistration
)
from offle_assistant.auth import (
    hash_password,
    verify_password,
    create_access_token
)
import offle_assistant.database as database
# from offle_assistant.database import (
#     create_user_in_db,
#     get_user_by_email,
#     get_default_group
# )
from offle_assistant.dependencies import get_db

auth_router = APIRouter()


@auth_router.post("/register")
async def register_user(
    user: UserRegistration,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Registers a new user with hashed password."""
    existing_user = await database.get_user_by_email(
        user_email=user.email,
        db=db
    )
    if existing_user:  # Checks if a user exists by email
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_user = await database.get_user_by_username(
        username=user.username,
        db=db
    )
    if existing_user:  # Checks if a user exists by username
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )

    # PROBLEM BELOW: This should really be an atomic operation.
    # If the server goes down before creating the user but after
    # creating the group, then you won't be able to create the user.
    # The solution is to wrap this all up in a transaction. But it
    # requires some planning to set up a replica set.

    default_group_dict = await database.get_default_group(db)
    default_group: GroupModel = GroupModel(**default_group_dict)

    existing_group = await database.get_group_by_name(
        group_name=user.username,
        db=db
    )

    if existing_group:  # Checks if a group exists by group name
        raise HTTPException(
            status_code=400,
            detail="Group already exists for this username."
        )
    user_group: GroupModel = GroupModel(
        name=user.username,
        description="Default user group"
    )
    user_group_id = await database.create_group(
        group=user_group,
        db=db
    )

    if not user_group_id:
        raise HTTPException(
            status_code=400,
            detail="Could not create user group."
        )

    default_group_name = default_group.name
    user_group_name = user_group.name

    # Create a new user.
    hashed_password = hash_password(user.password)
    new_user = UserModel(
        email=user.email,
        hashed_password=hashed_password,
        username=user.username,
        groups=[default_group_name, user_group_name],
        role="user"
    )

    # Plug the user into the database
    inserted_id = await database.create_user(
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
    user: UserLogin,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Authenticates a user and returns a JWT token."""

    # Find user by email
    db_user = await database.get_user_by_email(
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

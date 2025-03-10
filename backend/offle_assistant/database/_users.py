from typing import Dict, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.results import UpdateResult, DeleteResult

from offle_assistant.models import (
    UserModel,
    Role
)


############################
# CREATE
############################


async def create_user_in_db(
    new_user: UserModel,
    db: AsyncIOMotorDatabase
) -> ObjectId:
    """
        Adds a new user to the db. Returns the new id.
    """
    result = await db.users.insert_one(
        new_user.model_dump(exclude={"id"})
    )
    return result.inserted_id


############################
# Retrieve
############################


async def get_admin_exists(db: AsyncIOMotorDatabase) -> bool:
    admin_user = await db.users.find_one({"role": "admin"})
    if admin_user:
        return True
    else:
        return False


async def get_user_by_id(
    user_id: str,
    db: AsyncIOMotorDatabase
) -> Optional[Dict]:
    """Fetch a user from the database by their _id."""
    return await db.users.find_one({"_id": ObjectId(user_id)})


async def get_user_by_email(
    user_email: str,
    db: AsyncIOMotorDatabase
) -> Optional[Dict]:
    """Fetch a user from the database by their _id."""
    return await db.users.find_one({"email": user_email})


############################
# Update
############################


async def update_user_role_in_db(
    user_id: str,
    new_role: Role,
    db: AsyncIOMotorDatabase
) -> UpdateResult:
    """Updates a user's role."""
    return await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"role": new_role}}
    )


async def update_user_in_db(
    user_id: str,
    updates: dict,
    db: AsyncIOMotorDatabase
) -> UpdateResult:
    updated = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": updates}
    )

    return updated


############################
# Delete
############################


async def delete_user_in_db(
    user_id: str,
    db: AsyncIOMotorDatabase
) -> DeleteResult:
    """Deletes a user by id."""
    return await db.users.delete_one({"_id": ObjectId(user_id)})

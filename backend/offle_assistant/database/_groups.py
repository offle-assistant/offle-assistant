from typing import Dict, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.results import UpdateResult, DeleteResult

from offle_assistant.models import (
    GroupModel,
)


############################
# CREATE
############################


async def create_group(
    group: GroupModel,
    db: AsyncIOMotorDatabase
) -> ObjectId:
    """
        Adds a new group to the database. Returns the new id
    """
    result = await db.groups.insert_one(
        group.model_dump(exclude={"id"})
    )
    return result.inserted_id


############################
# Retrieve
############################


DEFAULT_GROUP_NAME = "default"


async def get_default_group(db: AsyncIOMotorDatabase):
    """Fetch the default group, or create it if it doesn't exist."""
    group = await db.groups.find_one({"name": DEFAULT_GROUP_NAME})

    if not group:
        # Create default group if it doesn't exist
        group_data = {
            "name": DEFAULT_GROUP_NAME,
            "description": "Default group for all users"
        }
        insert_result = await db.groups.insert_one(group_data)
        group = {**group_data, "_id": insert_result.inserted_id}

    return group


async def get_group_by_id(
    group_id: str,
    db: AsyncIOMotorDatabase
) -> Optional[Dict]:
    """Fetch a user from the database by their _id."""
    return await db.groups.find_one({"_id": ObjectId(group_id)})


async def get_group_by_name(
    group_name: str,
    db: AsyncIOMotorDatabase
) -> Optional[Dict]:
    """Fetch a user from the database by their _id."""
    return await db.groups.find_one({"name": group_name})


############################
# Update
############################


async def update_group_by_id(
    group_id: str,
    updates: dict,
    db: AsyncIOMotorDatabase
) -> UpdateResult:
    updated = await db.groups.update_one(
        {"_id": ObjectId(group_id)},
        {"$set": updates}
    )

    return updated


async def update_group_by_name(
    group_name: str,
    updates: dict,
    db: AsyncIOMotorDatabase
) -> UpdateResult:
    updated = await db.groups.update_one(
        {"name": ObjectId(group_name)},
        {"$set": updates}
    )

    return updated


############################
# Delete
############################


async def delete_group_by_id(
    group_id: str,
    db: AsyncIOMotorDatabase
) -> DeleteResult:
    """Deletes a user by id."""
    return await db.groups.delete_one({"_id": ObjectId(group_id)})


async def delete_group_by_name(
    group_name: str,
    db: AsyncIOMotorDatabase
) -> DeleteResult:
    """Deletes a user by name."""
    return await db.groups.delete_one({"name": ObjectId(group_name)})

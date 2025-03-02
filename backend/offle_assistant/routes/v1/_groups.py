import logging

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError

from offle_assistant.models import GroupModel, UserModel, GroupUpdateModel
from offle_assistant.auth import admin_required, get_current_user
from offle_assistant.dependencies import (
    get_db
)
import offle_assistant.database as database


groups_router = APIRouter()


@groups_router.get("/{group_identifier}", response_model=GroupModel)
async def get_group_by_identifier(
    group_identifier: str,
    user_model: UserModel = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Returns a persona by id."""

    if ObjectId.is_valid(group_identifier):
        group_dict: dict = await database.get_group_by_id(
            group_id=group_identifier,
            db=db
        )

    else:
        group_dict: dict = await database.get_group_by_name(
            group_name=group_identifier,
            db=db
        )

    if not group_dict:
        raise HTTPException(status_code=404, detail="Group not found")

    try:
        group_model: GroupModel = GroupModel(**group_dict)
    except ValidationError as e:
        raise HTTPException(
            status_code=500, detail=f"Invalid group data in DB: {e}"
        )

    return group_model


@groups_router.post("/create")
async def create_group(
    group: GroupModel,
    user: UserModel = Depends(admin_required),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Allows an admin to create a group."""

    try:
        group_id = await database.create_group(
            group=group,
            db=db
        )

        return {
            "message": "Group created successfully",
            "group_id": str(group_id)
        }

    except DuplicateKeyError:
        error_message = "Group name must be unique"
        logging.error(error_message)
        raise HTTPException(status_code=400, detail=error_message)


@groups_router.post("/update/{group_id}")
async def update_group(
    group_id: str,
    updates: GroupUpdateModel,
    db: AsyncIOMotorDatabase = Depends(get_db)
):

    group = await database.get_group_by_id(
        group_id=group_id,
        db=db
    )
    if not group:
        error_message = "Group not found"
        logging.error(error_message)
        raise HTTPException(status_code=404, detail=error_message)

    update_data = updates.model_dump(exclude_unset=True, exclude_none=True)

    update_success = await database.update_group(
        group_id=group_id,
        updates=update_data,
        db=db
    )

    if update_success.modified_count == 0:
        error_message = "No changes were made"
        logging.warning(error_message)
        raise HTTPException(status_code=400, detail=error_message)

    return {"message": "Group updated successfully"}


@groups_router.post("/delete/{group_id}")
async def delete_group(
    group_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    success = await database.delete_group(
        group_id=group_id,
        db=db
    )

    if not success:
        error_message = "Group not found. No changes were made"
        logging.error(error_message)
        raise HTTPException(status_code=404, detail=error_message)

    return {"message": "Group deleted successfully"}

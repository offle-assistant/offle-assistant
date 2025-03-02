from typing import Optional
import logging

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import ValidationError

from offle_assistant.models import GroupModel, UserModel
from offle_assistant.auth import admin_required
from offle_assistant.dependencies import (
    get_db
)
from offle_assistant.database import (
    get_group_by_id,
    create_group,
    delete_group,
    update_group
)


groups_router = APIRouter()


@groups_router.get("/{group_id}", response_model=GroupModel)
async def get_group(
    group_id: str,
    user_model: UserModel = Depends(admin_required),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Returns a persona by id."""

    group_dict: dict = await get_group_by_id(
        group_id=group_id,
        db=db
    )
    if not group_dict:
        raise HTTPException(status_code=404, detail="Group not found")

    try:
        group_model: GroupModel = GroupModel(**group_dict)
    except ValidationError as e:
        raise HTTPException(
            status_code=500, detail=f"Invalid persona data in DB: {e}"
        )

    return group_model


@groups_router.post("/build")
async def create_persona(
    group: GroupModel,
    user: UserModel = Depends(admin_required),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Allows a builder or admin to create a persona."""

    group_id = await create_group(
        group=group,
        db=db
    )

    return {
        "message": "Persona created successfully",
        "group_id": str(group_id)
    }

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase

from offle_assistant.auth import admin_required
import offle_assistant.database as database
from offle_assistant.dependencies import get_db
from offle_assistant.models import (
    Role,
)

admin_router = APIRouter()


##########################################
# USER OPERATIONS
##########################################

class RoleUpdateRequest(BaseModel):
    new_role: str


@admin_router.delete("/users/{user_id}/delete")
async def delete_user(
    user_id: str,
    admin: dict = Depends(admin_required),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Allows an admin to delete a user."""
    deleted = await database.delete_user_by_id(
        user_id=user_id,
        db=db
    )

    if deleted.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


@admin_router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role_update: RoleUpdateRequest,
    admin: dict = Depends(admin_required),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    new_role: Role = role_update.new_role

    """Allows an admin to change a user's role."""
    if new_role not in Role.__args__:
        raise HTTPException(status_code=400, detail="Invalid role")

    update_success = await database.update_user_role_by_id(
        user_id=user_id,
        new_role=new_role,
        db=db
    )

    if update_success.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": f"User role updated to {new_role}"}


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str


@admin_router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    admin: dict = Depends(admin_required),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Allows an admin to fetch all users."""
    users = await db.users.find(
        {}, {"_id": 1, "username": 1, "email": 1, "role": 1}
    ).to_list(length=None)

    if not users:
        raise HTTPException(status_code=404, detail="No users found")

    # Convert ObjectId to string
    return [
        {"id": str(user["_id"]),
         "username": user["username"],
         "email": user["email"],
         "role": user["role"]} for user in users
    ]

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from offle_assistant.mongo import users_collection
from offle_assistant.auth import admin_required
from offle_assistant.models import Role
from offle_assistant.database import (
    delete_user_in_db,
    update_user_role_in_db
)

admin_router = APIRouter()


class RoleUpdateRequest(BaseModel):
    new_role: Role


@admin_router.delete("/users/{user_id}/delete")
async def delete_user(user_id: str, admin: dict = Depends(admin_required)):
    """Allows an admin to delete a user."""
    deleted = await delete_user_in_db(user_id)

    if deleted.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


@admin_router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role_update: RoleUpdateRequest,
    admin: dict = Depends(admin_required)
):
    new_role: Role = role_update.new_role

    """Allows an admin to change a user's role."""
    if new_role not in Role.__args__:
        raise HTTPException(status_code=400, detail="Invalid role")

    update_success = update_user_role_in_db(user_id, new_role)

    if update_success.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": f"User role updated to {new_role}"}

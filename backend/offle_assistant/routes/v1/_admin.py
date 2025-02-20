from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from offle_assistant.database import users_collection
from offle_assistant.auth import admin_required
from offle_assistant.models import Role

admin_router = APIRouter()


class RoleUpdateRequest(BaseModel):
    new_role: Role


@admin_router.delete("/users/{user_id}")
async def delete_user(user_id: str, admin: dict = Depends(admin_required)):
    """Allows an admin to delete a user."""
    deleted = await users_collection.delete_one({"_id": ObjectId(user_id)})
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

    updated = await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"role": new_role}}
    )
    if updated.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": f"User role updated to {new_role}"}

from fastapi import APIRouter, Depends
from offle_assistant.auth import get_current_user


users_router = APIRouter()


@users_router.get("/me")
async def get_current_user_profile(user: dict = Depends(get_current_user)):
    """Returns the currently authenticated user's profile."""
    return {
        "user_id": str(user["_id"]),
        "email": user["email"],
        "username": user["username"]
    }

from fastapi import APIRouter, Depends
from offle_assistant.auth import get_current_user
from offle_assistant.models import UserModel


users_router = APIRouter()


@users_router.get("/me")
async def get_current_user_profile(
    user: UserModel = Depends(get_current_user)
):
    """Returns the currently authenticated user's profile."""
    return {
        "user_id": str(user.id),
        "email": user.email,
        "role": user.role,
        "username": user.username,
        "personas": user.personas,
    }

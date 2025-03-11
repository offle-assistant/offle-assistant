import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from motor.motor_asyncio import AsyncIOMotorDatabase

from offle_assistant.auth import get_current_user
from offle_assistant.models import (
    UserModel,
    MessageHistoryModel
)
import offle_assistant.database as database
from offle_assistant.dependencies import (
    get_db
)

message_history_router = APIRouter()


@message_history_router.get(
    "/{message_history_id}",
    response_model=MessageHistoryModel
)
async def get_message_history(
    message_history_id: str,
    user_model: UserModel = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    message_history_dict = (
        await database.get_message_history_by_id(
            message_history_id=message_history_id,
            db=db
        )
    )

    if not message_history_dict:
        raise HTTPException(
            status_code=404,
            detail="Message History not found"
        )

    try:
        message_hist: MessageHistoryModel = MessageHistoryModel(
            **message_history_dict
        )
    except ValidationError as e:
        # Handle or log the validation error as needed
        raise HTTPException(
            status_code=500,
            detail=f"Invalid message_content data in DB: {e}"
        )

    return message_hist

import logging
from typing import List

from fastapi.responses import StreamingResponse
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    File,
    UploadFile,
    Form
)
from motor.motor_asyncio import AsyncIOMotorDatabase

from offle_assistant.models import UserModel
from offle_assistant.auth import admin_required, get_current_user
from offle_assistant.dependencies import (
    get_db
)
import offle_assistant.database as database


documents_router = APIRouter()


@documents_router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    description: str = Form(...),
    tags: List[str] = Form([]),
    groups: List[str] = Form([]),
    user_model: UserModel = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> dict:
    """Handles file uploads"""

    try:
        file_id = await database.upload_file(
            file,
            description=description,
            groups=groups,
            tags=tags,
            user_id=user_model.id,
            user_groups=user_model.groups,
            db=db
        )
    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail="User doesn't have permissions to upload to this group"
        )

    return {"file_id": file_id, "message": "Successfully uploaded file"}


@documents_router.get("/download/{file_id}")
async def download_document(
    file_id: str,
    user_model: UserModel = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Downloads a file from GridFS using file_id"""

    try:
        streaming_response: StreamingResponse = (
            await database.download_file_by_id(
                file_id=file_id,
                user_groups=user_model.groups,
                db=db
            )
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail="User not in proper group to access file"
        )

    return streaming_response

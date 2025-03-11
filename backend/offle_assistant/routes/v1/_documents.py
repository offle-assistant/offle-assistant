import mimetypes
import logging
from typing import List

from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from bson import ObjectId
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    File,
    UploadFile,
    Form
)
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorGridFSBucket

from offle_assistant.models import FileMetadata, UserModel, GroupModel
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
    fs_bucket = AsyncIOMotorGridFSBucket(db)

    try:
        # Open the file stream from GridFS
        stream = await fs_bucket.open_download_stream(ObjectId(file_id))
    except Exception:
        raise HTTPException(status_code=404, detail="File not found")

    # Get filename and content type from metadata
    file_doc = await db["fs.files"].find_one({"_id": ObjectId(file_id)})
    filename = file_doc["filename"] if file_doc else f"{file_id}.bin"

    file_groups: List[str] = file_doc.get("metadata", {}).get("groups", [])

    user_groups: List[str] = user_model.groups

    # Nifty way of seeing if there is a common member between 2 lists
    has_permission = bool(set(file_groups) & set(user_groups))

    if not has_permission:
        raise HTTPException(
            status_code=403, detail="User not in proper group to access file"
        )

    content_type = file_doc.get("metadata", {}).get("content_type")
    if not content_type:
        content_type, _ = mimetypes.guess_type(filename)
    if not content_type:
        content_type = "application/octet-stream"  # Fallback

    return StreamingResponse(
        stream,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

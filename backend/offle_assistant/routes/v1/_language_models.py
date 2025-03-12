from typing import Dict

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.results import DeleteResult

from offle_assistant.auth import admin_required, get_current_user
import offle_assistant.database as database
from offle_assistant.dependencies import (
    get_db,
    get_llm_client,
)
from offle_assistant.models import (
    LanguageModelsCollection,
    ModelDetails,
    UserModel
)
from offle_assistant.llm_client import LLMClient
from offle_assistant.utils import (
    retrieve_available_models
)

models_router = APIRouter()


@models_router.get(
    "/available",
    response_model=LanguageModelsCollection
)
async def get_available_models(
    admin: dict = Depends(admin_required),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
        This is for retrieving all models available models.
        That is, the models which exist but are not necessarily
        available to the users.
    """

    models: LanguageModelsCollection = retrieve_available_models()
    return models


@models_router.get(
    "/available/refresh",
    response_model=LanguageModelsCollection
)
async def refresh_available_models(
    admin: dict = Depends(admin_required),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    models: LanguageModelsCollection = retrieve_available_models(
        force_update=True
    )
    return models


@models_router.post("/allowed")
async def add_user_model(
    model_details: ModelDetails,
    admin: dict = Depends(admin_required),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
        This adds a model to the database of models that
        are allowed for use by the users.
    """
    model_id = await database.add_model(
        llm=model_details,
        db=db
    )

    return {
        "message": "Model added successfully",
        "model_id": model_id
    }


@models_router.post("/allowed/pull")
async def pull_allowed_models(
    llm_client: LLMClient = Depends(get_llm_client),
    admin: Dict = Depends(admin_required),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
        When a model is set as allowed in the database,
        it also needs to get pulled down to local storage
        before it can be used. This route pulls down the
        models.
    """
    allowed_models: LanguageModelsCollection = (
        await database.get_allowed_models(
            db=db
        )
    )

    llm_client.update_models(
        language_models=allowed_models
    )
    success = await llm_client.pull_models()

    if success:
        return {
            "message": "Models pulled successfully",
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="Unable to pull models."
        )


@models_router.delete("/allowed/{model_id}")
async def delete_allowed_model_by_id(
    model_id: str,
    admin: UserModel = Depends(admin_required),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Deletes an allowed model from the database by its ObjectId.
    """
    if not ObjectId.is_valid(model_id):
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

    delete_result: DeleteResult = await database.delete_model_by_id(
        model_id=model_id,
        db=db
    )

    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Model not found")

    return {"message": "Model deleted successfully"}


@models_router.get("/allowed", response_model=LanguageModelsCollection)
async def get_allowed_models(
    user_model: UserModel = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        allowed_models = await database.get_allowed_models(db=db)

        if allowed_models is None:
            return LanguageModelsCollection(models=[])

        return allowed_models

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve models: {str(e)}"
        )

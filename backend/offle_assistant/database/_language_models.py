from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.results import UpdateResult, DeleteResult

from offle_assistant.models import (
    LanguageModelsCollection,
    # TagInfo,
    ModelDetails
)


############################
# CREATE
############################


async def add_model(
    llm: ModelDetails,
    db: AsyncIOMotorDatabase
) -> ObjectId:
    """
        Adds a new model entry to the database.
    """
    result = await db.allowed_models.insert_one(
        llm.model_dump(exclude={"id"})
    )
    return result.inserted_id


############################
# Retrieve
############################


async def get_allowed_models(
    db: AsyncIOMotorDatabase
) -> LanguageModelsCollection:
    """
        Fetch all Available Models
    """
    models = await db.allowed_models.find({}).to_list(None)
    language_models: LanguageModelsCollection = LanguageModelsCollection(
        models=models
    )
    return language_models


############################
# Delete
############################


async def delete_model_by_id(
    model_id: str,
    db: AsyncIOMotorDatabase
) -> DeleteResult:
    """Deletes a model from the allowed_models db"""
    return await db.allowed_models.delete_one({"_id": ObjectId(model_id)})

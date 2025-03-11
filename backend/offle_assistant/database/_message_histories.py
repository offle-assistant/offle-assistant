from typing import Dict, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.results import UpdateResult, DeleteResult

from offle_assistant.models import (
    MessageHistoryModel,
    MessageContent,
)

############################
# CREATE
############################


async def create_message_history(
    db: AsyncIOMotorDatabase,
    new_message_history_entry: Optional[MessageHistoryModel] = None,
) -> ObjectId:
    if new_message_history_entry is None:
        new_message_history_entry = MessageHistoryModel(
            title="Default Title",
            description="Default Description",
        )

    result = await db.message_histories.insert_one(
        new_message_history_entry.model_dump(exclude={"id"})
    )
    return result.inserted_id


############################
# RETRIEVE
############################


async def get_message_history_by_id(
    message_history_id: str,
    db: AsyncIOMotorDatabase
) -> Optional[Dict]:
    """Get a message history object"""
    return await db.message_histories.find_one(
        {"_id": ObjectId(message_history_id)}
    )


async def get_message_history_without_message_chain_by_id(
    message_history_id: str,
    db: AsyncIOMotorDatabase
) -> Optional[Dict]:
    """

    Get a message history object but without the message chain.
    This is basically a lightweight version of
    get_message_history_entry_by_id()

    """

    query = {"_id": ObjectId(message_history_id)}
    projection = {"messages": 0}
    retrieved_message_history: dict = await db.message_histories.find_one(
        query,
        projection
    )

    if not retrieved_message_history:
        return None

    return MessageHistoryModel(**retrieved_message_history)


async def get_message_history_list_by_user_id(
    user_id: str,
    persona_id: str,
    db: AsyncIOMotorDatabase
) -> Optional[Dict]:
    """
        Get message history information between a given persona
        and a given user. This omits the actual message chain
        to avoid pulling huge amounts of text all at once. After
        the user decides which message chain they want to pick
        back up with, you can use get_message_history_entry_by_id
        to get the full message history chain for that id.

        This will return None if there is no history to retrieve
    """
    query = {"_id": ObjectId(user_id)}
    projection = {f"persona_message_history.{persona_id}": 1}

    # This returns the user with only the persona_message_history key
    retrieved_user: list = await db.users.find_one(
        query,
        projection
    )
    if not retrieved_user:
        # Couldn't find a user by that id.
        return None

    message_history = retrieved_user.get(
        "persona_message_history",
        {}
    ).get(persona_id, [])

    return message_history


############################
# UPDATE
############################


async def update_message_history_by_id(
    message_history_id: str,
    updates: dict,
    db: AsyncIOMotorDatabase
) -> UpdateResult:
    update_success = await db.message_histories.update_one(
        {"_id": ObjectId(message_history_id)},
        {"$set": updates}
    )
    return update_success


async def append_message_to_message_history_by_id(
    message_history_id: str,
    message: MessageContent,
    db: AsyncIOMotorDatabase
):
    message_history: MessageHistoryModel = (
        await get_message_history_by_id(
            message_history_id=message_history_id,
            db=db
        )
    )

    message_history["messages"].append(message.model_dump())
    success = await update_message_history_by_id(
        message_history_id=message_history_id,
        updates=message_history,
        db=db
    )

    return success


############################
# DELETE
############################


async def delete_message_history_by_id(
    message_history_id: str,
    db: AsyncIOMotorDatabase
) -> DeleteResult:
    delete_result = await db.message_histories.delete_one(
        {"_id": ObjectId(message_history_id)}
    )
    return delete_result

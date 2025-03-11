import pickle

import redis
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from offle_assistant.persona import Persona
from offle_assistant.models import PersonaModel, MessageHistoryModel
import offle_assistant.database as database
# from offle_assistant.database import (
#     get_persona_by_id,
#     get_message_history_entry_by_id
# )

redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)


class SessionManager:
    @staticmethod
    async def get_persona_instance(
        user_id: ObjectId,
        persona_id: ObjectId,
        message_history_id: ObjectId,
        db: AsyncIOMotorDatabase
    ) -> Persona:
        """Retrieve persona from Redis or create a new one if needed."""

        # This also needs the message_id key concatenated to it.
        persona_key = f"persona:{user_id}:{persona_id}:{message_history_id}"

        # Walrus ;)
        if (cached_persona := redis_client.get(persona_key)) is not None:
            return pickle.loads(cached_persona)

        persona_dict: dict = await database.get_persona_by_id(
            persona_id,
            db=db
        )

        persona_dict["_id"] = str(persona_dict["_id"])
        persona_dict["user_id"] = str(persona_dict["user_id"])
        persona_dict["creator_id"] = str(persona_dict["creator_id"])
        persona_model: PersonaModel = PersonaModel(**persona_dict)
        message_history_dict = await database.get_message_history_by_id(
            message_history_id,
            db=db
        )

        message_history_dict["_id"] = str(message_history_dict["_id"])
        message_history_model: MessageHistoryModel = MessageHistoryModel(
            **message_history_dict
        )

        # If persona doesn't exist, create a new one
        new_persona: Persona = Persona(
            persona_model=persona_model,
            message_chain=message_history_model.messages
        )

        serialized_persona = pickle.dumps(new_persona)
        redis_client.set(persona_key, serialized_persona, ex=3600)  # 1hr
        return new_persona

    @staticmethod
    def save_persona_instance(
        user_id: str,
        persona_id: str,
        message_history_id: str,
        persona: Persona
    ):
        """Store the updated persona in Redis."""
        persona_key = f"persona:{user_id}:{persona_id}:{message_history_id}"
        serialized_persona = pickle.dumps(persona)
        redis_client.set(persona_key, serialized_persona, ex=3600)


class PersonaManager:
    @staticmethod
    def save_persona_instance(user_id: str, persona: Persona):
        """Store the updated persona in Redis as a pickled object."""
        persona_key = f"persona:{user_id}:{persona.persona_id}"
        serialized_data = pickle.dumps(persona)
        redis_client.set(persona_key, serialized_data, ex=3600)

    @staticmethod
    def get_persona_instance(user_id: str, persona_id: str) -> Persona | None:
        """Retrieve the pickled persona from Redis."""
        persona_key = f"persona:{user_id}:{persona_id}"
        raw_data = redis_client.get(persona_key)
        if raw_data is None:
            return None
        return pickle.loads(raw_data)

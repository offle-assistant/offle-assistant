import redis

from offle_assistant.persona import Persona
from offle_assistant.config import PersonaConfig

redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)


class SessionManager:
    @staticmethod
    def get_persona(
        user_id: str,
        persona_config: PersonaConfig
    ) -> Persona:
        """Retrieve persona from Redis or create a new one if needed."""
        persona_id = persona_config.persona_id
        persona_key = f"persona:{user_id}:{persona_id}"  # Unique key

        if (cached_persona := redis_client.get(persona_key)) is not None:
            return Persona.deserialize(cached_persona)  # Restore persona

        # If persona doesn't exist, create a new one
        new_persona: Persona = Persona(
            persona_id=persona_id,
            name=persona_config.name,
            description=persona_config.description,
            db_collections=persona_config.rag.collections,
            system_prompt=persona_config.system_prompt,
            model=persona_config.model,
            temperature=persona_config.temperature
        )
        redis_client.set(persona_key, new_persona.serialize(), ex=3600)  # 1hr
        return new_persona

    @staticmethod
    def save_persona(user_id: str, persona: Persona):
        """Store the updated persona in Redis."""
        persona_key = f"persona:{user_id}:{persona.persona_id}"
        redis_client.set(persona_key, persona.serialize(), ex=3600)

from httpx import AsyncClient

import pytest
from fastapi.encoders import jsonable_encoder

from offle_assistant.models import PersonaModel
from offle_assistant.main import app, create_default_admin
from offle_assistant.mongo import db

from .common import (
    create_test_user,
    get_default_admin_token,
    login_user,
    get_test_user_token,
    get_builder_token
)


@pytest.mark.asyncio(loop_scope="session")
async def test_create_persona_success():
    async with AsyncClient(app=app, base_url="http://test") as client:
        builder_token = await get_builder_token(client)
        print("TOKEN: ", builder_token)
        headers = {"Authorization": f"Bearer {builder_token}"}

        persona_model: PersonaModel = PersonaModel(
            name="Rick",
            description="Just a man.",
        )
        persona_model.created_at = jsonable_encoder(persona_model.created_at)
        payload = persona_model.model_dump()

        response = await client.post(
            "/personas/build",
            json=payload,
            headers=headers
        )

        assert response.status_code == 200

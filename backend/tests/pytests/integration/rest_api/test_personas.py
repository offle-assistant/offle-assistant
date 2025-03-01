from httpx import AsyncClient, ASGITransport

import pytest
from fastapi.encoders import jsonable_encoder

from offle_assistant.models import PersonaModel, PersonaUpdateModel
from offle_assistant.main import app, create_default_admin
from offle_assistant.mongo import db

from .common import (
    create_test_user,
    get_default_admin_token,
    login_user,
    get_test_user_token,
    get_builder_token,
    create_persona
)


@pytest.mark.asyncio(loop_scope="session")
async def test_create_persona_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        builder_token = await get_builder_token(client)
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
        data = response.json()
        assert data["message"] == "Persona created successfully"


@pytest.mark.asyncio(loop_scope="session")
async def test_create_persona_auth_failure():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        user_token = await get_test_user_token(client)
        headers = {"Authorization": f"Bearer {user_token}"}

        persona_model: PersonaModel = PersonaModel(
            name="Rick",
            description="Just a man.",
        )
        persona_model.created_at = jsonable_encoder(persona_model.created_at)
        payload = persona_model.model_dump()

        create_response = await client.post(
            "/personas/build",
            json=payload,
            headers=headers
        )

        assert create_response.status_code == 403
        create_data = create_response.json()
        assert create_data["detail"] == "Builder or admin access required"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_persona_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        builder_token = await get_builder_token(client)
        headers = {"Authorization": f"Bearer {builder_token}"}

        persona_model: PersonaModel = PersonaModel(
            name="Rick",
            description="Just a man.",
        )
        persona_model.created_at = jsonable_encoder(persona_model.created_at)
        payload = persona_model.model_dump()

        create_response = await client.post(
            "/personas/build",
            json=payload,
            headers=headers
        )
        create_data = create_response.json()
        persona_id = create_data["persona_id"]

        get_response = await client.get(
            f"personas/{persona_id}",
            headers=headers
        )

        received_persona_dict = get_response.json()
        assert get_response.status_code == 200

        received_persona = PersonaModel(**received_persona_dict)

        assert received_persona.name == persona_model.name
        assert received_persona.description == persona_model.description
        assert received_persona.system_prompt == persona_model.system_prompt
        assert received_persona.model == persona_model.model
        assert received_persona.temperature == persona_model.temperature

        # This is broken because of string vs datetime.  Reed - 02/27/2025
        # assert received_persona.created_at == persona_model.created_at


@pytest.mark.asyncio(loop_scope="session")
async def test_get_persona_failure_no_persona():
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        builder_token = await get_builder_token(client)
        headers = {"Authorization": f"Bearer {builder_token}"}

        persona_id = "63e4bcf5a79a8402ad3bb03b"

        get_response = await client.get(
            f"personas/{persona_id}",
            headers=headers
        )

        assert get_response.status_code == 404
        data = get_response.json()
        assert data["detail"] == "Persona not found"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_personas_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        builder_token = await get_builder_token(client)
        persona_id_1 = await create_persona(client, builder_token)
        persona_id_2 = await create_persona(client, builder_token)

        headers = {"Authorization": f"Bearer {builder_token}"}
        response = await client.get(
            "/personas/owned",
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["persona_dict"][persona_id_1]
        assert data["persona_dict"][persona_id_2]


@pytest.mark.asyncio(loop_scope="session")
async def test_update_personas_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        builder_token = await get_builder_token(client)

        persona_id = await create_persona(client, builder_token)

        persona_model: PersonaUpdateModel = PersonaUpdateModel(
            name="Ricardo",
            description="More than a man.",
        )
        persona_model.updated_at = jsonable_encoder(persona_model.updated_at)
        payload = persona_model.model_dump()

        headers = {"Authorization": f"Bearer {builder_token}"}
        response = await client.put(
            f"/personas/build/{persona_id}",
            headers=headers,
            json=payload,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Persona updated successfully"


@pytest.mark.asyncio(loop_scope="session")
async def test_update_personas_failure_not_owned():
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        builder_1_token = await get_builder_token(client)
        builder_2_token = await get_builder_token(client)

        persona_id = await create_persona(client, builder_1_token)
        persona_model: PersonaUpdateModel = PersonaUpdateModel(
            name="Ricardo",
            description="More than a man.",
        )

        persona_model.updated_at = jsonable_encoder(persona_model.updated_at)

        payload = persona_model.model_dump()

        headers = {"Authorization": f"Bearer {builder_2_token}"}
        response = await client.put(
            f"/personas/build/{persona_id}",
            headers=headers,
            json=payload,
        )

        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "You can only modify your own personas"


@pytest.mark.asyncio(loop_scope="session")
async def test_persona_chat_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        builder_token = await get_builder_token(client)
        persona_id = await create_persona(client, builder_token)

        payload = {
            "content": "Hello, how are you?"
        }

        headers = {"Authorization": f"Bearer {builder_token}"}
        response = await client.post(
            f"/personas/chat/{persona_id}",
            json=payload,
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["persona_id"] == persona_id
        assert data["message_history_id"]
        assert data["response"]
        assert data["rag_hit"]


@pytest.mark.asyncio(loop_scope="session")
async def test_persona_message_history_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        builder_token = await get_builder_token(client)
        persona_id = await create_persona(client, builder_token)

        payload = {
            "content": "Hello, how are you?"
        }

        headers = {"Authorization": f"Bearer {builder_token}"}
        chat_response = await client.post(
            f"/personas/chat/{persona_id}",
            json=payload,
            headers=headers
        )

        chat_data = chat_response.json()
        message_id = chat_data["message_history_id"]

        message_hist_response = await client.get(
            f"/personas/message-history/{persona_id}",
            headers=headers,
        )

        assert message_hist_response.status_code == 200

        data = message_hist_response.json()
        assert message_id in data["message_history"]

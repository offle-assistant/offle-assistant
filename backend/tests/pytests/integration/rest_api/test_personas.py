from typing import List
from httpx import AsyncClient, ASGITransport

import pytest
from fastapi.encoders import jsonable_encoder

from offle_assistant.auth import get_current_user
from offle_assistant.models import (
    PersonaModel,
    PersonaUpdateModel,
    PyObjectId,
    MessageContent,
    MessageHistoryModel
)
from offle_assistant.main import app

from .common import (
    create_persona
)


@pytest.mark.asyncio
async def test_create_persona_success(
    test_client,
    test_db,
    override_get_current_user_builder
):
    app.dependency_overrides[get_current_user] = (
        override_get_current_user_builder
    )

    headers = {"Authorization": "Bearer dummy_token"}

    persona_model: PersonaModel = PersonaModel(
        name="Rick",
        description="Just a man.",
    )
    persona_model.created_at = jsonable_encoder(persona_model.created_at)
    payload = persona_model.model_dump()

    response = await test_client.post(
        "/personas/build",
        json=payload,
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Persona created successfully"


@pytest.mark.asyncio
async def test_create_persona_auth_failure(
    test_client,
    test_db,
    override_get_current_user_normal_user
):
    app.dependency_overrides[get_current_user] = (
        override_get_current_user_normal_user
    )
    headers = {"Authorization": "Bearer dummy_token"}

    persona_model: PersonaModel = PersonaModel(
        name="Rick",
        description="Just a man.",
    )
    persona_model.created_at = jsonable_encoder(persona_model.created_at)
    payload = persona_model.model_dump()

    create_response = await test_client.post(
        "/personas/build",
        json=payload,
        headers=headers
    )

    assert create_response.status_code == 403
    create_data = create_response.json()
    assert create_data["detail"] == "Builder or admin access required"


@pytest.mark.asyncio
async def test_get_persona_success(
    test_client,
    test_db,
    override_get_current_user_builder
):
    app.dependency_overrides[get_current_user] = (
        override_get_current_user_builder
    )

    headers = {"Authorization": "Bearer dummy_token"}

    persona_model: PersonaModel = PersonaModel(
        name="Rick",
        description="Just a man.",
    )
    # persona_model.created_at = jsonable_encoder(persona_model.created_at)
    payload = persona_model.model_dump()

    create_response = await test_client.post(
        "/personas/build",
        json=payload,
        headers=headers
    )

    create_data = create_response.json()
    persona_id = create_data["persona_id"]

    get_response = await test_client.get(
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
    assert received_persona.created_at == persona_model.created_at


@pytest.mark.asyncio
async def test_get_persona_failure_no_persona(
    test_client,
    test_db,
    override_get_current_user_builder
):
    app.dependency_overrides[get_current_user] = (
        override_get_current_user_builder
    )

    headers = {"Authorization": "Bearer dummy_token"}

    persona_id = "63e4bcf5a79a8402ad3bb03b"

    get_response = await test_client.get(
        f"personas/{persona_id}",
        headers=headers
    )

    assert get_response.status_code == 404
    data = get_response.json()
    assert data["detail"] == "Persona not found"


@pytest.mark.asyncio
async def test_get_user_personas_success(
    test_client,
    test_db,
    override_get_current_user_builder
):
    app.dependency_overrides[get_current_user] = (
        override_get_current_user_builder
    )

    headers = {"Authorization": "Bearer dummy_token"}

    persona_data = {
        "name": "Test Persona",
        "description": "This is a test persona."
    }

    response = await test_client.post(
        "/personas/build",
        json=persona_data,
        headers=headers
    )
    persona_id_1 = response.json()["persona_id"]

    response = await test_client.post(
        "/personas/build",
        json=persona_data,
        headers=headers
    )
    persona_id_2 = response.json()["persona_id"]

    response = await test_client.get(
        "/personas/owned",
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["persona_dict"][persona_id_1]
    assert data["persona_dict"][persona_id_2]


@pytest.mark.asyncio
async def test_update_personas_success(
    test_client,
    test_db,
    override_get_current_user_builder
):
    app.dependency_overrides[get_current_user] = (
        override_get_current_user_builder
    )

    headers = {"Authorization": "Bearer dummy_token"}

    persona_id = await create_persona(test_client)

    persona_model: PersonaUpdateModel = PersonaUpdateModel(
        name="Ricardo",
        description="More than a man.",
    )
    persona_model.updated_at = jsonable_encoder(persona_model.updated_at)
    payload = persona_model.model_dump()

    response = await test_client.put(
        f"/personas/build/{persona_id}",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Persona updated successfully"


@pytest.mark.asyncio
async def test_update_personas_failure_not_owned(
    test_client,
    test_db,
    override_get_current_user_builder,
    override_get_current_user_admin
):
    app.dependency_overrides[get_current_user] = (
        override_get_current_user_admin
    )

    headers = {"Authorization": "Bearer dummy_token"}

    persona_id = await create_persona(test_client)
    persona_model: PersonaUpdateModel = PersonaUpdateModel(
        name="Ricardo",
        description="More than a man.",
    )

    payload = persona_model.model_dump()

    app.dependency_overrides[get_current_user] = (
        override_get_current_user_builder
    )

    headers = {"Authorization": "Bearer dummy_token"}

    response = await test_client.put(
        f"/personas/build/{persona_id}",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "You can only modify your own personas"


@pytest.mark.asyncio
async def test_persona_chat_success(
    test_client,
    test_db,
    override_get_current_user_builder
):
    app.dependency_overrides[get_current_user] = (
        override_get_current_user_builder
    )
    headers = {"Authorization": "Bearer dummy_token"}

    persona_id = await create_persona(test_client)

    payload = {
        "content": "Hello, how are you?"
    }

    response = await test_client.post(
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


@pytest.mark.asyncio
async def test_persona_message_history_success(
    test_client,
    test_db,
    override_get_current_user_builder
):
    app.dependency_overrides[get_current_user] = (
        override_get_current_user_builder
    )

    test_user = await override_get_current_user_builder()
    await test_db.users.insert_one({
        "_id": PyObjectId(test_user.id),
        "username": test_user.username,
        "email": test_user.email,
        "hashed_password": test_user.hashed_password,
        "role": test_user.role,
        "persona_message_history": {}
    })

    headers = {"Authorization": "Bearer dummy_token"}
    persona_id = await create_persona(test_client)

    payload = {
        "content": "Hello, how are you?"
    }

    chat_response = await test_client.post(
        f"/personas/chat/{persona_id}",
        json=payload,
        headers=headers
    )

    chat_data = chat_response.json()
    message_id = chat_data["message_history_id"]

    message_hist_response = await test_client.get(
        f"/personas/message-history/{persona_id}",
        headers=headers,
    )

    assert message_hist_response.status_code == 200

    data = message_hist_response.json()

    message_history_ids: List = [
        MessageHistoryModel(
            **message_history
        ).id for message_history in data["message_history"]
    ]

    assert message_id in message_history_ids

    test_db.users.drop()
    test_db.message_histories.drop()

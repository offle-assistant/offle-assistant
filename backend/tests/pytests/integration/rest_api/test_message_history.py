import pytest

from offle_assistant.auth import get_current_user
from offle_assistant.models import (
    PyObjectId,
    MessageHistoryModel
)
from offle_assistant.main import app

from .common import (
    create_persona
)


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

    message_history_full_response = await test_client.get(
        f"/message-history/{message_id}",
        headers=headers,
    )

    data = message_history_full_response.json()

    message_history_full: MessageHistoryModel = (
        MessageHistoryModel(
            **data
        )
    )

    assert message_id == message_history_full.id
    assert len(message_history_full.messages) > 0

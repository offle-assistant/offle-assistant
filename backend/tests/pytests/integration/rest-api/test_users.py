from httpx import AsyncClient

import pytest

from offle_assistant.main import app
from offle_assistant.mongo import db


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_by_id():
    async with AsyncClient(app=app, base_url="http://test") as client:
        await db.client.drop_database(db.name)

        reg_user_payload = {
            "email": "test_admin@example.com",
            "password": "securepassword",
        }

        reg_user_response = await client.post(
            "/auth/register", json=reg_user_payload
        )
        assert reg_user_response.status_code == 200
        data = reg_user_response.json()
        assert data["message"] == "User registered"

        login_response = await client.post(
            "/auth/login", json=reg_user_payload
        )

        assert login_response.status_code == 200
        data = login_response.json()
        assert data["access_token"]
        assert data["token_type"] == "bearer"

        user_token = data["access_token"]

        headers = {"Authorization": f"Bearer {user_token}"}

        get_user_response = await client.get("/users/me", headers=headers)

        assert get_user_response.status_code == 200
        data = get_user_response.json()
        assert data["email"] == reg_user_payload["email"]

from httpx import AsyncClient

import pytest

from offle_assistant.main import app
from offle_assistant.mongo import db

from .common import create_test_user, login_user


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_by_id():
    async with AsyncClient(app=app, base_url="http://test") as client:
        await db.client.drop_database(db.name)

        user_info = await create_test_user(client)

        email = user_info["email"]
        password = user_info["password"]

        user_token = await login_user(
            email=email,
            password=password,
            client=client
        )

        headers = {"Authorization": f"Bearer {user_token}"}

        get_user_response = await client.get("/users/me", headers=headers)

        assert get_user_response.status_code == 200
        data = get_user_response.json()
        assert data["email"] == email

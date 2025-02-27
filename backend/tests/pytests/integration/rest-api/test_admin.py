from httpx import AsyncClient

import pytest

from offle_assistant.main import app, create_default_admin
from offle_assistant.mongo import db


@pytest.mark.asyncio(loop_scope="session")
async def test_default_admin():
    await create_default_admin()
    async with AsyncClient(app=app, base_url="http://test") as client:
        default_admin_payload = {
            # "username": "admin",
            "email": "admin@admin.com",
            "password": "admin",
        }

        login_response = await client.post(
            "/auth/login", json=default_admin_payload
        )

        assert login_response.status_code == 200
        data = login_response.json()
        assert data["access_token"]
        assert data["token_type"] == "bearer"


@pytest.mark.asyncio(loop_scope="session")
async def test_user_delete_auth_failure():
    async with AsyncClient(app=app, base_url="http://test") as client:
        await db.client.drop_database(db.name)
        reg_admin_payload = {
            "email": "test_admin@example.com",
            "password": "securepassword",
        }

        reg_admin_response = await client.post(
            "/auth/register", json=reg_admin_payload
        )
        assert reg_admin_response.status_code == 200
        data = reg_admin_response.json()
        assert data["message"] == "User registered"

        reg_user_payload = {
            "email": "test_user@example.com",
            "password": "securepassword",
        }

        reg_user_response = await client.post(
            "/auth/register", json=reg_user_payload)
        assert reg_user_response.status_code == 200
        data = reg_user_response.json()
        assert data["message"] == "User registered"
        user_id = data["user_id"]

        login_response = await client.post(
            "/auth/login", json=reg_admin_payload
        )

        assert login_response.status_code == 200
        data = login_response.json()
        assert data["access_token"]
        assert data["token_type"] == "bearer"

        admin_token = data["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}
        del_user_response = await client.delete(
            f"/users/{user_id}/delete",
            headers=headers
        )
        assert del_user_response.status_code == 405
        data = del_user_response.json()
        print("RESPONSE DATA: ", data)
        assert data["detail"] == "Method Not Allowed"

        await db.client.drop_database(db.name)

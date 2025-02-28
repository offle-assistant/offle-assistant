from httpx import AsyncClient, ASGITransport

import pytest

from offle_assistant.main import app
from offle_assistant.mongo import db


@pytest.mark.asyncio(loop_scope="session")
async def test_register_user():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await db.client.drop_database(db.name)
        payload = {
            "email": "test_user@example.com",
            "password": "securepassword"
        }

        response = await client.post("/auth/register", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User registered"
        await db.client.drop_database(db.name)


@pytest.mark.asyncio(loop_scope="session")
async def test_register_admin():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await db.client.drop_database(db.name)
        payload = {
            "email": "test_user@example.com",
            "password": "securepassword",
            "role": "admin"
        }

        response = await client.post("/auth/register", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User registered"
        await db.client.drop_database(db.name)


@pytest.mark.asyncio(loop_scope="session")
async def test_login_user_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await db.client.drop_database(db.name)
        payload = {
            "email": "test_user@example.com",
            "password": "securepassword",
        }

        register_response = await client.post("/auth/register", json=payload)
        assert register_response.status_code == 200
        data = register_response.json()
        assert data["message"] == "User registered"

        login_response = await client.post("/auth/login", json=payload)
        assert login_response.status_code == 200
        data = login_response.json()
        assert data["access_token"]
        assert data["token_type"] == "bearer"

        await db.client.drop_database(db.name)


@pytest.mark.asyncio(loop_scope="session")
async def test_login_user_failure():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await db.client.drop_database(db.name)
        payload = {
            "email": "test_user@example.com",
            "password": "securepassword",
        }

        register_response = await client.post("/auth/register", json=payload)
        assert register_response.status_code == 200
        data = register_response.json()
        assert data["message"] == "User registered"

        bad_payload = {
            "email": "test_user@example.com",
            "password": "wrong_password",
        }
        login_response = await client.post("/auth/login", json=bad_payload)
        assert login_response.status_code == 401
        data = login_response.json()
        assert data["detail"] == "Invalid email or password"

        await db.client.drop_database(db.name)

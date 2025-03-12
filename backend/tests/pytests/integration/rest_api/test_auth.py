from httpx import AsyncClient, ASGITransport

import pytest

from offle_assistant.main import app
from offle_assistant.auth import (
    get_current_user,
)


@pytest.mark.asyncio
async def test_register_user(
    test_client,
    test_db,
):
    payload = {
        "username": "test_user",
        "email": "test_user@example.com",
        "password": "securepassword"
    }

    response = await test_client.post("/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User registered"
    await test_db.users.drop()


@pytest.mark.asyncio
async def test_register_user_failure_duplicate_username(
    test_client,
    test_db,
):
    payload_1 = {
        "email": "test_user@example.com",
        "username": "rich",
        "password": "securepassword",
    }

    payload_2 = {
        "email": "test2_user@example.com",
        "username": "rich",
        "password": "securepassword",
    }

    response = await test_client.post("/auth/register", json=payload_1)
    response = await test_client.post("/auth/register", json=payload_2)

    assert response.status_code == 400
    # assert response.status_code == 200
    # data = response.json()
    # assert data["message"] == "User registered"
    # await test_db.users.drop()


@pytest.mark.asyncio
async def test_login_user_success(
    test_client,
    test_db,
    override_get_current_user_normal_user
):
    await test_db.users.drop()
    app.dependency_overrides[get_current_user] = (
        override_get_current_user_normal_user
    )

    payload = {
        "username": "test_user",
        "email": "test_user@example.com",
        "password": "securepassword",
    }

    register_response = await test_client.post("/auth/register", json=payload)
    assert register_response.status_code == 200
    data = register_response.json()
    assert data["message"] == "User registered"

    login_response = await test_client.post("/auth/login", json=payload)
    assert login_response.status_code == 200
    data = login_response.json()
    assert data["access_token"]
    assert data["token_type"] == "bearer"

    await test_db.users.drop()


@pytest.mark.asyncio
async def test_login_user_failure(
    test_client,
    test_db,
    override_get_current_user_normal_user
):
    await test_db.users.drop()

    payload = {
        "username": "test_user",
        "email": "test_user@example.com",
        "password": "securepassword",
    }

    register_response = await test_client.post("/auth/register", json=payload)
    assert register_response.status_code == 200
    data = register_response.json()
    assert data["message"] == "User registered"

    bad_payload = {
        "email": "test_user@example.com",
        "password": "wrong_password",
    }
    login_response = await test_client.post("/auth/login", json=bad_payload)
    assert login_response.status_code == 401
    data = login_response.json()
    assert data["detail"] == "Invalid email or password"

    await test_db.users.drop()

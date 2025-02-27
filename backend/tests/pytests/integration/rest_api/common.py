from uuid import uuid1

from offle_assistant.main import create_default_admin


async def login_user(
    email,
    password,
    client
) -> str:
    """ Logs in a user, returns the auth token """
    login_user_payload = {"email": email, "password": password}

    login_response = await client.post(
        "/auth/login", json=login_user_payload
    )

    data = login_response.json()

    user_token = data["access_token"]
    return user_token


async def create_test_user(client) -> str:
    uuid_str = uuid1()
    user_email = f"{uuid_str}@example.com"
    password = "securepassword"

    reg_user_payload = {
        "email": user_email,
        "password": password,
    }

    reg_user_response = await client.post(
        "/auth/register", json=reg_user_payload)
    data = reg_user_response.json()
    return {
        "user_id": data["user_id"],
        "email": user_email,
        "password": password
    }


async def get_default_admin_token(client) -> str:
    await create_default_admin()
    default_admin_payload = {
        "email": "admin@admin.com",
        "password": "admin",
    }
    login_response = await client.post(
        "/auth/login", json=default_admin_payload
    )

    data = login_response.json()
    return data["access_token"]

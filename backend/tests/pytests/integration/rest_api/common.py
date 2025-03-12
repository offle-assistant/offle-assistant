from uuid import uuid1

from fastapi.encoders import jsonable_encoder

from offle_assistant.main import create_default_admin
from offle_assistant.models import PersonaModel


async def login_user(
    email,
    password,
    test_client,
    test_db,
) -> str:
    """ Logs in a user, returns the auth token """
    login_user_payload = {"email": email, "password": password}
    login_response = await test_client.post(
        "/auth/login", json=login_user_payload
    )

    data = login_response.json()

    user_token = data["access_token"]
    return user_token


async def get_test_user_token(test_client, test_db) -> str:
    user_info = await create_test_user(test_db)

    email = user_info["email"]
    password = user_info["password"]

    user_token = await login_user(
        email=email,
        password=password,
        test_client=test_client,
        test_db=test_db
    )

    return user_token


async def create_test_user(test_client) -> str:
    uuid_str = str(uuid1())
    user_email = f"{uuid_str}@example.com"
    username = uuid_str[:29]
    password = "securepassword"

    reg_user_payload = {
        "username": username,
        "email": user_email,
        "password": password,
    }

    reg_user_response = await test_client.post(
        "/auth/register", json=reg_user_payload)
    data = reg_user_response.json()
    return {
        "user_id": data["user_id"],
        "email": user_email,
        "password": password
    }


async def get_builder_token(test_db) -> str:
    """

    I will admit this is janky. But I needed a way to get
    a builder to test the authentication for this role.

    """

    # Create a default user
    builder_info = await create_test_user(test_db)
    builder_id = builder_info["user_id"]
    builder_email = builder_info["email"]
    builder_password = builder_info["password"]

    # promote that user
    admin_token = await get_default_admin_token(test_db)
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {"new_role": "builder"}

    await test_db.put(
        f"/admin/users/{builder_id}/role",
        json=payload,
        headers=headers
    )

    # Log the user in and return their token
    builder_token = await login_user(
        email=builder_email,
        password=builder_password,
        client=test_db
    )

    return builder_token


async def get_default_admin_token(test_db) -> str:
    await create_default_admin()
    default_admin_payload = {
        "email": "admin@admin.com",
        "password": "admin",
    }
    login_response = await test_db.post(
        "/auth/login", json=default_admin_payload
    )

    data = login_response.json()
    return data["access_token"]


async def create_persona(test_client) -> str:

    persona_model: PersonaModel = PersonaModel(
        name="Rick",
        description="Just a man.",
    )

    payload = persona_model.model_dump()

    headers = {"Authorization": "Bearer dummy_token"}
    create_response = await test_client.post(
        "/personas/build",
        json=payload,
        headers=headers
    )

    create_data = create_response.json()
    persona_id = create_data["persona_id"]

    return str(persona_id)

from httpx import AsyncClient

import pytest

from offle_assistant.main import app, create_default_admin
from offle_assistant.mongo import db

from .common import (
    create_test_user,
    get_default_admin_token,
    login_user
)


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

        # Create the user who is going to attempt a delete.
        user_1_info = await create_test_user(client)
        user_1_email = user_1_info["email"]
        user_1_password = user_1_info["password"]

        # Create the user who we're going to try to delete
        user_2_info = await create_test_user(client)
        user_2_id = user_2_info["user_id"]

        # Attempt the delete
        login_token = await login_user(
            email=user_1_email,
            password=user_1_password,
            client=client
        )

        headers = {"Authorization": f"Bearer {login_token}"}
        del_user_response = await client.delete(
            f"/admin/users/{user_2_id}/delete",
            headers=headers
        )
        assert del_user_response.status_code == 403
        data = del_user_response.json()
        assert data["detail"] == "Admin access required"

        await db.client.drop_database(db.name)


@pytest.mark.asyncio(loop_scope="session")
async def test_user_delete_auth_success():
    async with AsyncClient(app=app, base_url="http://test") as client:
        user_info = await create_test_user(client)
        user_id = user_info["user_id"]

        admin_token = await get_default_admin_token(client)
        headers = {"Authorization": f"Bearer {admin_token}"}
        del_user_response = await client.delete(
            f"/admin/users/{user_id}/delete",
            headers=headers
        )

        assert del_user_response.status_code == 200
        data = del_user_response.json()
        assert data["message"] == "User deleted successfully"

        await db.client.drop_database(db.name)


@pytest.mark.asyncio(loop_scope="session")
async def test_user_delete_user_id_does_not_exist():
    async with AsyncClient(app=app, base_url="http://test") as client:
        user_id = "63e4bcf5a79a8402ad3bb03b"

        admin_token = await get_default_admin_token(client)
        headers = {"Authorization": f"Bearer {admin_token}"}

        # This should fail since it's a fake user
        del_user_response = await client.delete(
            f"/admin/users/{user_id}/delete",
            headers=headers
        )
        assert del_user_response.status_code == 404
        data = del_user_response.json()
        assert data["detail"] == "User not found"

        await db.client.drop_database(db.name)


@pytest.mark.asyncio(loop_scope="session")
async def test_promote_user_success():
    async with AsyncClient(app=app, base_url="http://test") as client:
        user_info = await create_test_user(client)
        user_id = user_info["user_id"]

        new_roles = ["admin", "builder"]
        for new_role in new_roles:
            admin_token = await get_default_admin_token(client)
            headers = {"Authorization": f"Bearer {admin_token}"}
            payload = {"new_role": f"{new_role}"}
            user_update_response = await client.put(
                f"/admin/users/{user_id}/role",
                json=payload,
                headers=headers
            )

            assert user_update_response.status_code == 200

            data = user_update_response.json()
            assert data["message"] == f"User role updated to {new_role}"


@pytest.mark.asyncio(loop_scope="session")
async def test_promote_user_failure_not_admin():
    async with AsyncClient(app=app, base_url="http://test") as client:
        user_info = await create_test_user(client)
        user_id = user_info["user_id"]

        auth_user_info = await create_test_user(client)
        auth_email = auth_user_info["email"]
        auth_password = auth_user_info["password"]

        auth_token = await login_user(
            email=auth_email,
            password=auth_password,
            client=client
        )

        new_role = "admin"
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"new_role": f"{new_role}"}
        user_update_response = await client.put(
            f"/admin/users/{user_id}/role",
            json=payload,
            headers=headers
        )

        assert user_update_response.status_code == 403

        data = user_update_response.json()
        assert data["detail"] == "Admin access required"


@pytest.mark.asyncio(loop_scope="session")
async def test_promote_user_failure_no_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        user_id = "63e4bcf5a79a8402ad3bb03b"

        new_roles = ["admin", "builder"]
        for new_role in new_roles:
            admin_token = await get_default_admin_token(client)
            headers = {"Authorization": f"Bearer {admin_token}"}
            payload = {"new_role": f"{new_role}"}
            user_update_response = await client.put(
                f"/admin/users/{user_id}/role",
                json=payload,
                headers=headers
            )

            assert user_update_response.status_code == 404

            data = user_update_response.json()
            assert data["detail"] == "User not found"


@pytest.mark.asyncio(loop_scope="session")
async def test_promote_user_failure_invalid_role():
    async with AsyncClient(app=app, base_url="http://test") as client:
        user_info = await create_test_user(client)
        user_id = user_info["user_id"]

        new_role = "fake_role"

        admin_token = await get_default_admin_token(client)
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {"new_role": f"{new_role}"}
        user_update_response = await client.put(
            f"/admin/users/{user_id}/role",
            json=payload,
            headers=headers
        )

        assert user_update_response.status_code == 400

        data = user_update_response.json()
        assert data["detail"] == "Invalid role"

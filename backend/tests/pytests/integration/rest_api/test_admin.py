import pytest

from offle_assistant.main import app, create_default_admin
from offle_assistant.auth import (
    get_current_user,
)

from .common import (
    create_test_user,
)


# @pytest.mark.asyncio
# async def test_default_admin(test_client, test_db):
#     await create_default_admin()
#     default_admin_payload = {
#         # "username": "admin",
#         "email": "admin@admin.com",
#         "password": "admin",
#     }
#
#     login_response = await test_client.post(
#         "/auth/login", json=default_admin_payload
#     )
#
#     assert login_response.status_code == 200
#     data = login_response.json()
#     assert data["access_token"]
#     assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_user_delete_auth_failure(
    test_client,
    test_db,
    override_get_current_user_normal_user
):
    app.dependency_overrides[get_current_user] = (
        override_get_current_user_normal_user
    )

    headers = {"Authorization": "Bearer dummy_token"}

    # Create the user who we're going to try to delete
    user_info = await create_test_user(test_client)
    user_id = user_info["user_id"]

    del_user_response = await test_client.delete(
        f"/admin/users/{user_id}/delete",
        headers=headers
    )
    assert del_user_response.status_code == 403
    data = del_user_response.json()
    assert data["detail"] == "Admin access required"


@pytest.mark.asyncio
async def test_user_delete_auth_success(
    test_client,
    test_db,
    override_get_current_user_admin
):
    app.dependency_overrides[get_current_user] = (
        override_get_current_user_admin
    )

    user_info = await create_test_user(test_client)
    user_id = user_info["user_id"]

    headers = {"Authorization": "Bearer dummy_token"}
    del_user_response = await test_client.delete(
        f"/admin/users/{user_id}/delete",
        headers=headers
    )

    assert del_user_response.status_code == 200
    data = del_user_response.json()
    assert data["message"] == "User deleted successfully"


@pytest.mark.asyncio
async def test_user_delete_user_id_does_not_exist(
    test_client,
    test_db,
    override_get_current_user_admin
):
    app.dependency_overrides[get_current_user] = (
        override_get_current_user_admin
    )
    user_id = "63e4bcf5a79a8402ad3bb03b"

    headers = {"Authorization": "Bearer dummy_token"}

    # This should fail since it's a fake user
    del_user_response = await test_client.delete(
        f"/admin/users/{user_id}/delete",
        headers=headers
    )
    assert del_user_response.status_code == 404
    data = del_user_response.json()
    assert data["detail"] == "User not found"


@pytest.mark.asyncio
async def test_promote_user_success(
    test_client,
    test_db,
    override_get_current_user_admin
):
    app.dependency_overrides[get_current_user] = (
        override_get_current_user_admin
    )
    user_info = await create_test_user(test_client)
    user_id = user_info["user_id"]

    new_roles = ["admin", "builder"]
    for new_role in new_roles:
        headers = {"Authorization": "Bearer dummy_token"}
        payload = {"new_role": f"{new_role}"}
        user_update_response = await test_client.put(
            f"/admin/users/{user_id}/role",
            json=payload,
            headers=headers
        )

        assert user_update_response.status_code == 200

        data = user_update_response.json()
        assert data["message"] == f"User role updated to {new_role}"


@pytest.mark.asyncio
async def test_promote_user_failure_not_admin(
    test_client,
    test_db,
    override_get_current_user_normal_user
):
    app.dependency_overrides[get_current_user] = (
        override_get_current_user_normal_user
    )

    user_info = await create_test_user(test_client)
    user_id = user_info["user_id"]

    new_role = "admin"
    headers = {"Authorization": "Bearer dummy_token"}
    payload = {"new_role": f"{new_role}"}
    user_update_response = await test_client.put(
        f"/admin/users/{user_id}/role",
        json=payload,
        headers=headers
    )

    assert user_update_response.status_code == 403

    data = user_update_response.json()
    assert data["detail"] == "Admin access required"


@pytest.mark.asyncio
async def test_promote_user_failure_no_user(
    test_client,
    test_db,
    override_get_current_user_admin
):
    app.dependency_overrides[get_current_user] = (
        override_get_current_user_admin
    )
    user_id = "63e4bcf5a79a8402ad3bb03b"

    new_roles = ["admin", "builder"]
    for new_role in new_roles:
        headers = {"Authorization": "Bearer dummy_token"}
        payload = {"new_role": f"{new_role}"}
        user_update_response = await test_client.put(
            f"/admin/users/{user_id}/role",
            json=payload,
            headers=headers
        )

        assert user_update_response.status_code == 404

        data = user_update_response.json()
        assert data["detail"] == "User not found"


@pytest.mark.asyncio
async def test_promote_user_failure_invalid_role(
    test_client,
    test_db,
    override_get_current_user_admin
):
    app.dependency_overrides[get_current_user] = (
        override_get_current_user_admin
    )
    user_info = await create_test_user(test_client)
    user_id = user_info["user_id"]

    new_role = "fake_role"

    headers = {"Authorization": "Bearer dummy_token"}
    payload = {"new_role": f"{new_role}"}
    user_update_response = await test_client.put(
        f"/admin/users/{user_id}/role",
        json=payload,
        headers=headers
    )

    assert user_update_response.status_code == 400

    data = user_update_response.json()
    assert data["detail"] == "Invalid role"

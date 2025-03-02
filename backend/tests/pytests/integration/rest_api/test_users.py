import pytest

from offle_assistant.auth import get_current_user
from offle_assistant.main import app


@pytest.mark.asyncio
async def test_get_current_user(
    test_client,
    test_db,
    override_get_current_user_normal_user
):
    app.dependency_overrides[get_current_user] = (
        override_get_current_user_normal_user
    )

    headers = {"Authorization": "Bearer dummy_token"}

    get_user_response = await test_client.get(
        "/users/me",
        headers=headers
    )

    assert get_user_response.status_code == 200


# @pytest.mark.asyncio
# async def test_get_user_by_id(test_client, test_db):
#     user_info = await create_test_user(
#         test_client=test_client,
#     )
#
#     email = user_info["email"]
#     password = user_info["password"]
#
#     headers = {"Authorization": "Bearer dummy_token"}
#
#     get_user_response = await test_client.get(
#         "/users/me",
#         headers=headers
#     )
#
#     assert get_user_response.status_code == 200
#     data = get_user_response.json()

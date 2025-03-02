import pytest

from offle_assistant.auth import get_current_user
from offle_assistant.models import GroupModel, GroupUpdateModel
from offle_assistant.main import app


@pytest.mark.asyncio
async def test_create_group_success(
    test_client,
    test_db,
    override_get_current_user_admin
):
    app.dependency_overrides[get_current_user] = (
        override_get_current_user_admin
    )

    headers = {"Authorization": "Bearer dummy_token"}

    group_model: GroupModel = GroupModel(
        name="default",
        description="Default group for all users"
    )

    payload = group_model.model_dump()

    response = await test_client.post(
        "/groups/create",
        json=payload,
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Group created successfully"


@pytest.mark.asyncio
async def test_create_group_failure_duplicate_name(
    test_client,
    test_db,
    override_get_current_user_admin
):
    app.dependency_overrides[get_current_user] = (
        override_get_current_user_admin
    )

    headers = {"Authorization": "Bearer dummy_token"}

    group_model: GroupModel = GroupModel(
        name="default",
        description="Default group for all users"
    )

    payload = group_model.model_dump()

    response = await test_client.post(
        "/groups/create",
        json=payload,
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Group created successfully"

    payload = group_model.model_dump()

    response = await test_client.post(
        "/groups/create",
        json=payload,
        headers=headers
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Group name must be unique"


@pytest.mark.asyncio
async def test_get_group_by_id_success(
    test_client,
    test_db,
    override_get_current_user_admin
):
    app.dependency_overrides[get_current_user] = (
        override_get_current_user_admin
    )

    headers = {"Authorization": "Bearer dummy_token"}

    group_model: GroupModel = GroupModel(
        name="default",
        description="Default group for all users"
    )

    payload = group_model.model_dump()

    create_response = await test_client.post(
        "/groups/create",
        json=payload,
        headers=headers
    )

    data = create_response.json()
    group_id = data["group_id"]

    get_response = await test_client.get(
        f"/groups/{group_id}",
        headers=headers
    )

    assert get_response.status_code == 200
    data = get_response.json()
    retrieved_group: GroupModel = GroupModel(**data)
    assert retrieved_group.name == group_model.name


@pytest.mark.asyncio
async def test_get_group_by_name_success(
    test_client,
    test_db,
    override_get_current_user_admin
):
    app.dependency_overrides[get_current_user] = (
        override_get_current_user_admin
    )

    headers = {"Authorization": "Bearer dummy_token"}

    group_model: GroupModel = GroupModel(
        name="default",
        description="Default group for all users"
    )

    payload = group_model.model_dump()

    create_response = await test_client.post(
        "/groups/create",
        json=payload,
        headers=headers
    )

    data = create_response.json()

    get_response = await test_client.get(
        f"/groups/{group_model.name}",
        headers=headers
    )

    assert get_response.status_code == 200
    data = get_response.json()
    retrieved_group: GroupModel = GroupModel(**data)
    assert retrieved_group.description == group_model.description


@pytest.mark.asyncio
async def test_delete_group_success(
    test_client,
    test_db,
    override_get_current_user_admin
):
    app.dependency_overrides[get_current_user] = (
        override_get_current_user_admin
    )

    headers = {"Authorization": "Bearer dummy_token"}

    group_model: GroupModel = GroupModel(
        name="default",
        description="Default group for all users"
    )

    payload = group_model.model_dump()

    response = await test_client.post(
        "/groups/create",
        json=payload,
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Group created successfully"

    group_id = data["group_id"]

    delete_response = await test_client.post(
        f"/groups/delete/{group_id}",
        headers=headers
    )

    assert delete_response.status_code == 200
    data = delete_response.json()
    assert data["message"] == "Group deleted successfully"


@pytest.mark.asyncio
async def test_update_group_success(
    test_client,
    test_db,
    override_get_current_user_admin
):
    app.dependency_overrides[get_current_user] = (
        override_get_current_user_admin
    )

    headers = {"Authorization": "Bearer dummy_token"}

    group_model: GroupModel = GroupModel(
        name="default",
        description="Default group for all users"
    )

    payload = group_model.model_dump()

    response = await test_client.post(
        "/groups/create",
        json=payload,
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Group created successfully"

    group_id = data["group_id"]

    group_model: GroupUpdateModel = GroupUpdateModel(
        name="New name",
    )

    payload = group_model.model_dump()

    response = await test_client.post(
        f"/groups/update/{group_id}",
        json=payload,
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Group updated successfully"

    get_response = await test_client.get(
        f"/groups/{group_id}",
        headers=headers
    )

    assert get_response.status_code == 200
    data = get_response.json()
    retrieved_group: GroupModel = GroupModel(**data)

    assert retrieved_group.name == "New name"

import pytest

from offle_assistant.main import app
from offle_assistant.auth import (
    get_current_user,
)


@pytest.mark.asyncio
async def test_upload_download_document(
    test_client,
    test_db,
    override_get_current_user_normal_user
):
    app.dependency_overrides[get_current_user] = (
        override_get_current_user_normal_user
    )

    headers = {"Authorization": "Bearer dummy_token"}

    file_content = b"Hello, GridFS!"

    files = {"file": ("test.txt", file_content, "text/plain")}
    data = {
        "description": "A file about nothing.",
        "tags": ["short", "nothing"],
    }

    upload_response = await test_client.post(
        "/documents/upload",
        files=files,
        data=data,
        headers=headers
    )

    assert upload_response.status_code == 200
    data = upload_response.json()
    file_id = data["file_id"]
    assert data["message"] == "Successfully uploaded file"

    download_response = await test_client.get(
        f"/documents/download/{file_id}",
    )
    assert download_response.status_code == 200
    assert download_response.content == file_content


@pytest.mark.asyncio
async def test_upload_document_failure_permission(
    test_client,
    test_db,
    override_get_current_user_normal_user
):
    app.dependency_overrides[get_current_user] = (
        override_get_current_user_normal_user
    )

    headers = {"Authorization": "Bearer dummy_token"}

    file_content = b"Hello, GridFS!"

    files = {"file": ("test.txt", file_content, "text/plain")}
    data = {
        "description": "A file about nothing.",
        "tags": ["short", "nothing"],
        "groups": ["admin"]
    }

    upload_response = await test_client.post(
        "/documents/upload",
        files=files,
        data=data,
        headers=headers
    )

    assert upload_response.status_code == 403
    data = upload_response.json()
    assert data["detail"] == (
        "User doesn't have permissions to upload to this group"
    )


@pytest.mark.asyncio
async def test_download_document_failure_permission(
    test_client,
    test_db,
    override_get_current_user_normal_user,
    override_get_current_user_admin,
):
    app.dependency_overrides[get_current_user] = (
        override_get_current_user_admin
    )

    headers = {"Authorization": "Bearer dummy_token"}

    file_content = b"Hello, GridFS!"

    files = {"file": ("test.txt", file_content, "text/plain")}
    data = {
        "description": "A file about nothing.",
        "tags": ["short", "nothing"],
        "groups": ["admin"]
    }

    upload_response = await test_client.post(
        "/documents/upload",
        files=files,
        data=data,
        headers=headers
    )

    assert upload_response.status_code == 200
    data = upload_response.json()
    file_id = data["file_id"]
    assert data["message"] == "Successfully uploaded file"

    app.dependency_overrides[get_current_user] = (
        override_get_current_user_normal_user
    )

    download_response = await test_client.get(
        f"/documents/download/{file_id}",
    )
    assert download_response.status_code == 403
    data = download_response.json()
    assert data["detail"] == "User not in proper group to access file"

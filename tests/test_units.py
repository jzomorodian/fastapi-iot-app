import pytest
from httpx import AsyncClient
from uuid import uuid4
from unittest.mock import AsyncMock

# --- Test Data ---

TEST_ID = uuid4()
TEST_UNIT_DATA = {
    'id': TEST_ID,
    'name': "TestUnit-A",
    'location': "Test Location",
    'is_active': True,
    'created_at': "2025-01-01T00:00:00+00:00"
}

# Note: fixtures are now in conftest.py

# --- Test Cases ---


@pytest.mark.asyncio
async def test_create_unit_success(
    client: AsyncClient,
    mock_unit_repo: AsyncMock,
    mock_db_connection
):
    """Test successful unit creation."""
    mock_unit_repo.create.return_value = TEST_UNIT_DATA

    response = await client.post(
        "/v1/units/",
        json={"name": "New Unit", "location": "Test Location"}
    )

    assert response.status_code == 201
    assert response.json()["name"] == "TestUnit-A"
    mock_unit_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_unit_conflict(
    client: AsyncClient,
    mock_unit_repo: AsyncMock,
    mock_db_connection
):
    """Test creating a unit with a duplicate name (conflict)."""
    mock_unit_repo.create.side_effect = ValueError("Unit name already exists.")

    response = await client.post(
        "/v1/units/",
        json={"name": "Existing Unit", "location": "Anywhere"}
    )

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_unit_by_id_success(
    client: AsyncClient,
    mock_unit_repo: AsyncMock,
    mock_db_connection
):
    """Test retrieving an existing unit by ID."""
    mock_unit_repo.get_by_id.return_value = TEST_UNIT_DATA

    response = await client.get(f"/v1/units/{TEST_ID}")

    assert response.status_code == 200
    assert response.json()["id"] == str(TEST_ID)
    mock_unit_repo.get_by_id.assert_called_once_with(TEST_ID)


@pytest.mark.asyncio
async def test_get_unit_not_found(
    client: AsyncClient,
    mock_unit_repo: AsyncMock,
    mock_db_connection
):
    """Test retrieving a unit that does not exist."""
    mock_unit_repo.get_by_id.return_value = None

    non_existent_id = uuid4()
    response = await client.get(f"/v1/units/{non_existent_id}")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_unit_success(
    client: AsyncClient,
    mock_unit_repo: AsyncMock,
    mock_db_connection
):
    """Test successful deletion of a unit."""
    mock_unit_repo.delete.return_value = True  # Indicates 1 row deleted

    response = await client.delete(f"/v1/units/{TEST_ID}")

    assert response.status_code == 204
    mock_unit_repo.delete.assert_called_once_with(TEST_ID)


@pytest.mark.asyncio
async def test_delete_unit_not_found(
    client: AsyncClient,
    mock_unit_repo: AsyncMock,
    mock_db_connection
):
    """Test deleting a unit that does not exist."""
    mock_unit_repo.delete.return_value = False  # Indicates 0 rows deleted

    response = await client.delete(f"/v1/units/{uuid4()}")

    assert response.status_code == 404

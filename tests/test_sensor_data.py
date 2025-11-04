import pytest
from uuid import UUID
from fastapi import FastAPI
from httpx import AsyncClient
# No schema imports needed for tests
from app.api.v1.endpoints.sensor_data import router as sensor_data_router


@pytest.fixture
def app(mock_db, mock_sensor_repo) -> FastAPI:
    """
    Create a FastAPI test application with the sensor data router.
    Uses the mock_db fixture that's already available.
    """
    app = FastAPI()
    app.include_router(sensor_data_router, prefix="/api/v1")
    return app


@pytest.fixture
def valid_sensor_data() -> dict:
    return {
        "unit_id": "123e4567-e89b-12d3-a456-426614174000",
        "temperature": 25.5,
        "humidity": 60.0,
        "status": "PENDING",
        "is_archived": False
    }


@pytest.mark.asyncio
async def test_create_sensor_data(
    app: FastAPI,
    client: AsyncClient,
    valid_sensor_data: dict
):
    """Test creating new sensor data."""
    response = await client.post(
        "/api/v1/sensor-data/",
        json=valid_sensor_data
    )
    assert response.status_code == 201

    data = response.json()
    assert isinstance(data["id"], str)
    assert UUID(data["id"])  # Verify it's a valid UUID
    assert data["temperature"] == valid_sensor_data["temperature"]
    assert data["humidity"] == valid_sensor_data["humidity"]
    assert data["status"] == valid_sensor_data["status"]
    assert data["is_archived"] == valid_sensor_data["is_archived"]
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_get_sensor_data(
    app: FastAPI,
    client: AsyncClient,
    valid_sensor_data: dict
):
    """Test retrieving sensor data by ID."""
    # First create a sensor data record
    response = await client.post(
        "/api/v1/sensor-data/",
        json=valid_sensor_data
    )
    created_data = response.json()
    sensor_data_id = created_data["id"]

    # Then retrieve it
    response = await client.get(f"/api/v1/sensor-data/{sensor_data_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == sensor_data_id
    assert data["temperature"] == valid_sensor_data["temperature"]
    assert data["humidity"] == valid_sensor_data["humidity"]


@pytest.mark.asyncio
async def test_list_sensor_data(app: FastAPI, client: AsyncClient):
    """Test listing all sensor data records."""
    response = await client.get("/api/v1/sensor-data/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_list_sensor_data_by_unit(
    app: FastAPI,
    client: AsyncClient,
    valid_sensor_data: dict
):
    """Test listing sensor data filtered by unit."""
    # First create some sensor data
    await client.post("/api/v1/sensor-data/", json=valid_sensor_data)

    # Then retrieve by unit_id
    unit_id = valid_sensor_data["unit_id"]
    response = await client.get(f"/api/v1/sensor-data/?unit_id={unit_id}")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert all(item["unit_id"] == unit_id for item in data)


@pytest.mark.asyncio
async def test_update_sensor_data(
    app: FastAPI,
    client: AsyncClient,
    valid_sensor_data: dict
):
    """Test updating sensor data."""
    # First create a sensor data record
    response = await client.post(
        "/api/v1/sensor-data/",
        json=valid_sensor_data
    )
    sensor_data_id = response.json()["id"]

    # Update the data
    update_data = {
        "temperature": 26.5,
        "status": "VALIDATED"
    }
    response = await client.put(
        f"/api/v1/sensor-data/{sensor_data_id}",
        json=update_data
    )
    assert response.status_code == 200

    data = response.json()
    assert data["temperature"] == update_data["temperature"]
    assert data["status"] == update_data["status"]
    assert data["humidity"] == valid_sensor_data["humidity"]  # Unchanged field


@pytest.mark.asyncio
async def test_delete_sensor_data(
    app: FastAPI,
    client: AsyncClient,
    valid_sensor_data: dict
):
    """Test deleting sensor data."""
    # First create a sensor data record
    response = await client.post(
        "/api/v1/sensor-data/",
        json=valid_sensor_data
    )
    sensor_data_id = response.json()["id"]

    # Delete it
    response = await client.delete(f"/api/v1/sensor-data/{sensor_data_id}")
    assert response.status_code == 204

    # Verify it's deleted
    get_response = await client.get(f"/api/v1/sensor-data/{sensor_data_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_get_unit_statistics(
    app: FastAPI,
    client: AsyncClient,
    valid_sensor_data: dict
):
    """Test retrieving unit statistics."""
    # Create some sensor data for the unit
    await client.post("/api/v1/sensor-data/", json=valid_sensor_data)

    # Get statistics
    unit_id = valid_sensor_data["unit_id"]
    url = f"/api/v1/sensor-data/unit/{unit_id}/statistics"
    response = await client.get(url)
    assert response.status_code == 200

    stats = response.json()
    assert stats["unit_id"] == unit_id
    assert "avg_temperature" in stats
    assert "avg_humidity" in stats
    assert "total_readings" in stats
    assert "validated_readings" in stats
    assert "archived_readings" in stats


@pytest.mark.asyncio
async def test_archive_sensor_data(
    app: FastAPI,
    client: AsyncClient,
    valid_sensor_data: dict
):
    """Test archiving sensor data."""
    # First create a sensor data record
    response = await client.post(
        "/api/v1/sensor-data/",
        json=valid_sensor_data
    )
    sensor_data_id = response.json()["id"]

    # Archive it
    response = await client.post(
        f"/api/v1/sensor-data/{sensor_data_id}/archive"
    )
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == sensor_data_id
    assert data["is_archived"] is True


@pytest.mark.asyncio
async def test_create_sensor_data_invalid_unit(
    app: FastAPI,
    client: AsyncClient
):
    """Test creating sensor data with invalid unit ID."""
    # Test with invalid data but valid UUID format
    invalid_data = {
        # Non-existent but valid UUID
        "unit_id": "123e4567-e89b-12d3-a456-426614174999",
        "temperature": 25.5,
        "humidity": 60.0,
        "status": "PENDING",
        "is_archived": False
    }
    response = await client.post("/api/v1/sensor-data/", json=invalid_data)
    assert response.status_code == 404
    assert "does not exist" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_nonexistent_sensor_data(
    app: FastAPI,
    client: AsyncClient
):
    """Test retrieving non-existent sensor data."""
    fake_id = "123e4567-e89b-12d3-a456-426614174999"
    response = await client.get(f"/api/v1/sensor-data/{fake_id}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_nonexistent_sensor_data(
    app: FastAPI,
    client: AsyncClient
):
    """Test updating non-existent sensor data."""
    fake_id = "123e4567-e89b-12d3-a456-426614174999"
    update_data = {"temperature": 26.5}
    response = await client.put(
        f"/api/v1/sensor-data/{fake_id}",
        json=update_data
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_statistics_no_data(
    app: FastAPI,
    client: AsyncClient
):
    """Test getting statistics for a unit with no sensor data."""
    fake_unit_id = "123e4567-e89b-12d3-a456-426614174999"
    response = await client.get(
        f"/api/v1/sensor-data/unit/{fake_unit_id}/statistics"
    )
    assert response.status_code == 404
    assert "no sensor data found" in response.json()["detail"].lower()

# tests/conftest.py
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from fastapi import FastAPI
import asyncpg
from uuid import UUID


# Using pytest-asyncio's built-in event_loop fixture instead
# For module scope, use @pytest.mark.asyncio(scope="module") on test functions


@pytest_asyncio.fixture
async def mock_db():
    """Create a mock database connection."""
    mock_conn = AsyncMock()
    return mock_conn


@pytest_asyncio.fixture
async def mock_db_connection(mock_db, monkeypatch):
    """Provide a mock database connection for dependency injection."""
    async def _mock_pool():
        return mock_db

    # Patch the database pool getter used in the endpoints
    monkeypatch.setattr("app.core.database.get_db_pool", _mock_pool)
    return mock_db


@pytest_asyncio.fixture
async def app() -> FastAPI:
    """Create a FastAPI test application."""
    from app.main import app
    return app


@pytest_asyncio.fixture
async def client(app: FastAPI):
    """Create an async client for testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def mock_unit_repo(mocker):
    """Create a mock repository."""
    mock_repo = mocker.AsyncMock()

    # Configure default return values for async methods
    mock_repo.get_by_id.return_value = None  # Default: Unit not found
    mock_repo.create.return_value = None
    mock_repo.delete.return_value = False
    mock_repo.update.return_value = None

    # Patch the repository instantiation
    mocker.patch(
        'app.api.v1.endpoints.units.UnitRepository',
        return_value=mock_repo
    )

    return mock_repo


@pytest.fixture
def valid_sensor_data() -> dict:
    return {
        "unit_id": "123e4567-e89b-12d3-a456-426614174000",
        "temperature": 25.5,
        "humidity": 60.0,
        "status": "PENDING",
        "is_archived": False
    }


@pytest.fixture
def mock_sensor_repo(mocker, valid_sensor_data):
    """Create a mock sensor data repository with state management."""
    mock_repo = mocker.AsyncMock()

    # Store for keeping track of created/updated records
    stored_data = {}

    # Base record template
    base_record = {
        'id': '123e4567-e89b-12d3-a456-426614174000',
        'unit_id': valid_sensor_data["unit_id"],
        'temperature': valid_sensor_data["temperature"],
        'humidity': valid_sensor_data["humidity"],
        'status': valid_sensor_data["status"],
        'is_archived': valid_sensor_data["is_archived"],
        'timestamp': '2023-01-01T00:00:00'
    }

    # Mock get_by_id to return data from our store
    async def mock_get_by_id(id_):
        return stored_data.get(str(id_))
    mock_repo.get_by_id.side_effect = mock_get_by_id

    # Mock create to store and return created data
    async def mock_create(data):
        try:
            # Try to get the data as dict (support both v1 and v2)
            try:
                data_dict = data.model_dump()
            except AttributeError:
                data_dict = data.dict()

            # Check if unit exists
            if not isinstance(data.unit_id, UUID):
                raise ValueError("Invalid UUID format")

            unit_exists = await mock_repo.check_unit_exists(data.unit_id)
            if not unit_exists:
                raise asyncpg.exceptions.ForeignKeyViolationError()

            record = {**base_record, **data_dict}
            stored_data[str(record['id'])] = record
            return record
        except (ValueError, TypeError, AttributeError) as e:
            print(f"Create error: {e}")  # For debugging
            raise ValueError("Invalid data format")
    mock_repo.create.side_effect = mock_create

    # Mock update to modify stored data
    async def mock_update(id_, update_data):
        if str(id_) not in stored_data:
            return None
        try:
            # Try both Pydantic v2 and v1 methods
            try:
                data_dict = update_data.model_dump(exclude_unset=True)
            except AttributeError:
                data_dict = update_data.dict(exclude_unset=True)

            # Validate fields
            valid_fields = {"temperature", "humidity", "status", "is_archived"}
            if not all(k in valid_fields for k in data_dict.keys()):
                raise ValueError("Invalid fields in update")

            updated = {**stored_data[str(id_)], **data_dict}
            stored_data[str(id_)] = updated
            return updated
        except (ValueError, TypeError, AttributeError) as e:
            print(f"Update error: {e}")  # For debugging
            raise ValueError(str(e))
    mock_repo.update.side_effect = mock_update

    # Mock delete to remove from stored data
    async def mock_delete(id_):
        if str(id_) not in stored_data:
            return False
        del stored_data[str(id_)]
        return True
    mock_repo.delete.side_effect = mock_delete

    # Mock archive to update stored data
    async def mock_archive(id_):
        if str(id_) not in stored_data:
            return None
        stored_data[str(id_)]['is_archived'] = True
        return stored_data[str(id_)]
    mock_repo.archive_data.side_effect = mock_archive

    # Mock get_unit_statistics
    async def mock_get_stats(unit_id):
        try:
            unit_data = [d for d in stored_data.values() if str(
                d['unit_id']) == str(unit_id)]
            if not unit_data:
                return None

            validated = [d for d in unit_data if d['status'] == 'VALIDATED']
            archived = [d for d in unit_data if d['is_archived']]

            return {
                'unit_id': str(unit_id),
                'avg_temperature': sum(
                    d['temperature'] for d in unit_data) / len(unit_data),
                'avg_humidity': sum(
                    d['humidity'] for d in unit_data) / len(unit_data),
                'total_readings': len(unit_data),
                'validated_readings': len(validated),
                'archived_readings': len(archived)
            }
        except (ValueError, TypeError):
            raise ValueError("Invalid unit ID")
    mock_repo.get_unit_statistics.side_effect = mock_get_stats

    # Mock get_all
    async def mock_get_all(limit=100, offset=0, unit_id=None):
        if unit_id:
            return [d for d in stored_data.values()
                    if str(d['unit_id']) == str(unit_id)][offset:offset+limit]
        return list(stored_data.values())[offset:offset+limit]
    mock_repo.get_all.side_effect = mock_get_all

    # Mock check_unit_exists for foreign key validation
    async def mock_check_unit_exists(unit_id):
        try:
            str_unit_id = str(unit_id)
            return str_unit_id == valid_sensor_data["unit_id"]
        except (ValueError, TypeError):
            return False
    mock_repo.check_unit_exists = mock_check_unit_exists

    # Patch the repository instantiation
    mocker.patch(
        'app.api.v1.endpoints.sensor_data.SensorDataRepository',
        return_value=mock_repo
    )

    return mock_repo

# tests/conftest.py
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from app.main import app


@pytest.fixture(scope="module")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


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
async def client():
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

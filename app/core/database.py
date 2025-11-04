from contextlib import asynccontextmanager
import asyncpg
from app.core.config import settings
from typing import AsyncGenerator

# Global variable to hold the connection pool
pool: asyncpg.Pool | None = None


async def connect_db():
    """Initializes the PostgreSQL connection pool."""
    global pool
    try:
        pool = await asyncpg.create_pool(
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            min_size=5,
            max_size=20
        )
        print("--- Database connection pool created successfully ---")
    except Exception as e:
        print(f"--- FAILED to connect to the database: {e} ---")
        pool = None
        raise  # prevent app startup if DB not available


async def disconnect_db():
    """Closes the PostgreSQL connection pool."""
    global pool
    if pool:
        await pool.close()
        print("--- Database connection pool closed ---")


async def get_db_pool() -> AsyncGenerator[asyncpg.Pool, None]:
    """Dependency injector for database connection pool."""
    if not pool:
        # Should be handled by application startup, but good for safety
        await connect_db()
    yield pool


@asynccontextmanager
async def get_connection():
    """Dependency injector for database connection.

    Usage:
        @app.get("/endpoint")
        async def handler(conn=Depends(get_connection)):
            # Use the connection here
            result = await conn.fetch("SELECT * FROM table")
            return result
    """
    if not pool:
        await connect_db()
    async with pool.acquire() as connection:
        yield connection

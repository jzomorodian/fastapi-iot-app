from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.core.database import connect_db, disconnect_db
# Import endpoints
from app.api.v1.endpoints import units, sensor_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_db()
    yield
    # Shutdown
    await disconnect_db()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# --- API Routes ---
app.include_router(units.router, prefix=settings.API_V1_STR)
app.include_router(sensor_data.router, prefix=settings.API_V1_STR)


@app.get("/", include_in_schema=False)
def root():
    return {"message": settings.PROJECT_NAME, "docs": "/docs"}

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
import asyncpg
from app.core.database import get_db_pool
from app.crud.sensor_data_repo import SensorDataRepository
from app.schemas.sensor_data import (
    SensorData,
    SensorDataCreate,
    SensorDataUpdate,
    SensorDataStatistics
)

router = APIRouter(
    prefix="/sensor-data",
    tags=["Sensor Data (IoT Telemetry)"]
)


async def get_sensor_repo(
    pool: asyncpg.Pool = Depends(get_db_pool)
) -> SensorDataRepository:
    return SensorDataRepository(pool)


@router.get(
    "/",
    response_model=List[SensorData],
    summary="List all sensor data"
)
async def list_sensor_data(
    limit: int = 100,
    offset: int = 0,
    unit_id: Optional[UUID] = None,
    repo: SensorDataRepository = Depends(get_sensor_repo)
):
    """
    Retrieves a list of sensor data records with pagination support.
    Optionally filter by unit ID to get readings from a specific unit.
    """
    try:
        data = await repo.get_all(limit=limit, offset=offset, unit_id=unit_id)
        return [SensorData(**item) for item in data]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/",
    response_model=SensorData,
    status_code=status.HTTP_201_CREATED,
    summary="Create new sensor data"
)
async def create_sensor_data(
    data: SensorDataCreate,
    repo: SensorDataRepository = Depends(get_sensor_repo)
):
    """
    Creates a new sensor data record for a specific unit.
    The unit must exist in the system.
    """
    try:
        # Try to create the data
        new_data = await repo.create(data)
        if not new_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create sensor data due to an internal error."
            )
        return SensorData(**new_data)
    except (
        asyncpg.exceptions.ForeignKeyViolationError,
        asyncpg.exceptions.InvalidTextRepresentationError
    ):
        # Handle both FK violations and invalid UUID formats
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit does not exist"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{sensor_data_id}",
    response_model=SensorData,
    summary="Retrieve sensor data by ID"
)
async def get_sensor_data(
    sensor_data_id: UUID,
    repo: SensorDataRepository = Depends(get_sensor_repo)
):
    """
    Retrieves detailed information for a specific sensor data record
    using its UUID.
    """
    try:
        data = await repo.get_by_id(sensor_data_id)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sensor data with ID {sensor_data_id} not found."
            )
        return SensorData(**data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/unit/{unit_id}/statistics",
    response_model=SensorDataStatistics,
    summary="Get unit statistics"
)
async def get_unit_statistics(
    unit_id: UUID,
    repo: SensorDataRepository = Depends(get_sensor_repo)
):
    """
    Retrieves statistical information about sensor data for a specific unit.
    """
    try:
        stats = await repo.get_unit_statistics(unit_id)
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="no sensor data found"
            )
        return SensorDataStatistics(**stats)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put(
    "/{sensor_data_id}",
    response_model=SensorData,
    summary="Update sensor data"
)
async def update_sensor_data(
    sensor_data_id: UUID,
    data: SensorDataUpdate,
    repo: SensorDataRepository = Depends(get_sensor_repo)
):
    """
    Updates a sensor data record. Only provided fields will be updated.
    """
    try:
        # First check if record exists
        existing_data = await repo.get_by_id(sensor_data_id)
        if not existing_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sensor data with ID {sensor_data_id} not found."
            )

        updated_data = await repo.update(sensor_data_id, data)
        if not updated_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sensor data with ID {sensor_data_id} not found."
            )
        return SensorData(**updated_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except asyncpg.exceptions.ForeignKeyViolationError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit does not exist."
        )


@router.delete(
    "/{sensor_data_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete sensor data"
)
async def delete_sensor_data(
    sensor_data_id: UUID,
    repo: SensorDataRepository = Depends(get_sensor_repo)
):
    """
    Deletes a sensor data record from the system.
    """
    try:
        # First check if record exists
        existing_data = await repo.get_by_id(sensor_data_id)
        if not existing_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sensor data with ID {sensor_data_id} not found."
            )

        # Then try to delete it
        deleted = await repo.delete(sensor_data_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sensor data with ID {sensor_data_id} not found."
            )
        return  # Return None for 204 response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{sensor_data_id}/archive",
    response_model=SensorData,
    summary="Archive sensor data"
)
async def archive_sensor_data(
    sensor_data_id: UUID,
    repo: SensorDataRepository = Depends(get_sensor_repo)
):
    """
    Archives a sensor data record for historical reference.
    Archived records are still accessible but marked as archived.
    """
    try:
        # First check if record exists
        existing_data = await repo.get_by_id(sensor_data_id)
        if not existing_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sensor data with ID {sensor_data_id} not found."
            )

        archived_data = await repo.archive_data(sensor_data_id)
        if not archived_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sensor data with ID {sensor_data_id} not found."
            )

        # Convert the dict returned by the mock
        return SensorData.model_validate(archived_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

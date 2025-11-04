from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_connection
from app.crud.sensor_data_repo import SensorDataRepository
from app.schemas.sensor_data import (
    SensorData,
    SensorDataCreate,
    SensorDataUpdate,
    SensorDataStatistics
)

router = APIRouter()


@router.post("/sensor-data/", response_model=UUID, status_code=201)
async def create_sensor_data(
    data: SensorDataCreate,
    conn=Depends(get_connection)
):
    """
    Create new sensor data record.
    """
    repo = SensorDataRepository(conn)
    return await repo.create(data)


@router.get("/sensor-data/{sensor_data_id}", response_model=SensorData)
async def get_sensor_data(
    sensor_data_id: UUID,
    conn=Depends(get_connection)
):
    """
    Get a specific sensor data record by ID.
    """
    repo = SensorDataRepository(conn)
    data = await repo.get_by_id(sensor_data_id)
    if not data:
        raise HTTPException(status_code=404, detail="Sensor data not found")
    return data


@router.get("/sensor-data/", response_model=List[SensorData])
async def list_sensor_data(
    limit: int = 100,
    offset: int = 0,
    unit_id: Optional[UUID] = None,
    conn=Depends(get_connection)
):
    """
    List sensor data records, optionally filtered by unit ID.
    """
    repo = SensorDataRepository(conn)
    if unit_id:
        return await repo.get_by_unit(unit_id, limit, offset)
    return await repo.get_all(limit, offset)


@router.patch("/sensor-data/{sensor_data_id}", response_model=bool)
async def update_sensor_data(
    sensor_data_id: UUID,
    data: SensorDataUpdate,
    conn=Depends(get_connection)
):
    """
    Update a sensor data record.
    """
    repo = SensorDataRepository(conn)
    success = await repo.update(sensor_data_id, data)
    if not success:
        raise HTTPException(status_code=404, detail="Sensor data not found")
    return True


@router.delete("/sensor-data/{sensor_data_id}", response_model=bool)
async def delete_sensor_data(
    sensor_data_id: UUID,
    conn=Depends(get_connection)
):
    """
    Delete a sensor data record.
    """
    repo = SensorDataRepository(conn)
    success = await repo.delete(sensor_data_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sensor data not found")
    return True


@router.get(
    "/units/{unit_id}/statistics/",
    response_model=SensorDataStatistics
)
async def get_unit_statistics(
    unit_id: UUID,
    conn=Depends(get_connection)
):
    """
    Get statistical information about a unit's sensor data.
    """
    repo = SensorDataRepository(conn)
    stats = await repo.get_unit_statistics(unit_id)
    if not stats:
        raise HTTPException(
            status_code=404,
            detail="No sensor data found for this unit"
        )
    return stats


@router.post("/sensor-data/{sensor_data_id}/archive", response_model=bool)
async def archive_sensor_data(
    sensor_data_id: UUID,
    conn=Depends(get_connection)
):
    """
    Archive a sensor data record.
    """
    repo = SensorDataRepository(conn)
    success = await repo.archive_data(sensor_data_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sensor data not found")
    return True

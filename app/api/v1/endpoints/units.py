from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from app.schemas.unit import UnitCreate, UnitRead, UnitUpdate
from app.crud.unit_repo import UnitRepository
from app.core.database import get_db_pool
import asyncpg

router = APIRouter(prefix="/units", tags=["Units (Asset Management)"])

# Dependency function to provide a Repository instance


async def get_unit_repo(
        pool: asyncpg.Pool = Depends(get_db_pool)
) -> UnitRepository:
    return UnitRepository(pool)


@router.post(
    "/",
    response_model=UnitRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Unit"
)
async def create_unit(
    unit: UnitCreate,
    repo: UnitRepository = Depends(get_unit_repo)
):
    """Registers a new IoT unit in the system. The unit name must be unique."""
    try:
        new_unit = await repo.create(unit)
        if not new_unit:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create unit due to an internal error."
            )
        return UnitRead(**new_unit)
    except ValueError as e:  # Catches UniqueViolationError re-raised by repo
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/", response_model=List[UnitRead], summary="Retrieve all Units")
async def read_units(
    limit: int = 100, offset: int = 0,
    repo: UnitRepository = Depends(get_unit_repo)
):
    """Retrieves a list of all registered units, supporting pagination."""
    units_data = await repo.get_all(limit=limit, offset=offset)
    return [UnitRead(**data) for data in units_data]


@router.get(
    "/{unit_id}",
    response_model=UnitRead,
    summary="Retrieve a Unit by ID"
)
async def read_unit(
    unit_id: UUID,
    repo: UnitRepository = Depends(get_unit_repo)
):
    """
    Retrieves detailed information for a specific unit using its UUID.
    """
    unit_data = await repo.get_by_id(unit_id)
    if not unit_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Unit with ID {unit_id} not found.")
    return UnitRead(**unit_data)


@router.put(
    "/{unit_id}",
    response_model=UnitRead,
    summary="Update Unit details"
)
async def update_unit(
    unit_id: UUID,
    unit: UnitUpdate,
    repo: UnitRepository = Depends(get_unit_repo)
):
    """
    Updates the details of an existing unit.
    Note: Provide only the fields you wish to change.
    """
    try:
        updated_unit = await repo.update(unit_id, unit)
        if not updated_unit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Unit with ID {unit_id} not found.")
        return UnitRead(**updated_unit)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete(
    "/{unit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a Unit"
)
async def delete_unit(
    unit_id: UUID,
    repo: UnitRepository = Depends(get_unit_repo)
):
    """
    Deletes a unit from the system.
    Note: This will also delete all associated sensor data.
    """
    deleted = await repo.delete(unit_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Unit with ID {unit_id} not found.")
    return

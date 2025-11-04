from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

# --- Base Schemas ---


class UnitBase(BaseModel):
    name: str = Field(..., description="Unique name for the unit/asset.")
    location: str | None = Field(
        None,
        description="Physical location of the unit."
    )

# --- Request Schemas ---


class UnitCreate(UnitBase):
    pass

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Warehouse-A",
                "location": "North Dock"
            }
        }


class UnitUpdate(UnitBase):
    is_active: bool | None = Field(
        None,
        description="Status indicating if the unit is currently active."
    )

# --- Response Schemas ---


class UnitRead(UnitBase):
    id: UUID = Field(..., description="Unique identifier for the unit.")
    is_active: bool
    created_at: datetime

    # Allows mapping from database records (asyncpg.Record)
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "b08499c7-5e6a-4d9b-a7f4-21915f01198c",
                "name": "Warehouse-A",
                "location": "North Dock",
                "is_active": True,
                "created_at": "2025-01-01T10:00:00"
            }
        }

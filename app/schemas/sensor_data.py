from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class SensorDataBase(BaseModel):
    unit_id: UUID
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    status: str = Field(default="PENDING")
    is_archived: bool = Field(default=False)


class SensorDataCreate(SensorDataBase):
    pass


class SensorData(SensorDataBase):
    id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True


class SensorDataUpdate(BaseModel):
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    status: Optional[str] = None
    is_archived: Optional[bool] = None


class SensorDataStatistics(BaseModel):
    unit_id: UUID
    avg_temperature: Optional[float]
    avg_humidity: Optional[float]
    total_readings: int
    validated_readings: int
    archived_readings: int

from typing import List, Optional
from uuid import UUID, uuid4
from asyncpg import Connection
from app.schemas.sensor_data import (
    SensorDataCreate,
    SensorDataUpdate,
    SensorDataStatistics
)


class SensorDataRepository:
    def __init__(self, conn: Connection):
        self.conn = conn

    async def create(self, data: SensorDataCreate) -> UUID:
        query = """
            INSERT INTO sensor_data
                (id, unit_id, temperature, humidity, status, is_archived)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
        """
        record_id = uuid4()
        await self.conn.execute(
            query,
            record_id,
            data.unit_id,
            data.temperature,
            data.humidity,
            data.status,
            data.is_archived
        )
        return record_id

    async def get_by_id(self, sensor_data_id: UUID) -> Optional[dict]:
        query = "SELECT * FROM sensor_data WHERE id = $1"
        return await self.conn.fetchrow(query, sensor_data_id)

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[dict]:
        query = """
            SELECT * FROM sensor_data
            ORDER BY timestamp DESC
            LIMIT $1 OFFSET $2
        """
        return await self.conn.fetch(query, limit, offset)

    async def get_by_unit(
            self,
            unit_id: UUID,
            limit: int = 100,
            offset: int = 0
    ) -> List[dict]:
        query = """
            SELECT * FROM sensor_data
            WHERE unit_id = $1
            ORDER BY timestamp DESC
            LIMIT $2 OFFSET $3
        """
        return await self.conn.fetch(query, unit_id, limit, offset)

    async def update(
            self,
            sensor_data_id: UUID,
            data: SensorDataUpdate
    ) -> bool:
        update_fields = []
        values = []
        value_index = 1

        for field, value in data.dict(exclude_unset=True).items():
            if value is not None:
                update_fields.append(f"{field} = ${value_index}")
                values.append(value)
                value_index += 1

        if not update_fields:
            return False

        values.append(sensor_data_id)
        query = f"""
            UPDATE sensor_data
            SET {', '.join(update_fields)}
            WHERE id = ${value_index}
        """

        result = await self.conn.execute(query, *values)
        return result == "UPDATE 1"

    async def delete(self, sensor_data_id: UUID) -> bool:
        query = "DELETE FROM sensor_data WHERE id = $1"
        result = await self.conn.execute(query, sensor_data_id)
        return result == "DELETE 1"

    async def get_unit_statistics(
            self,
            unit_id: UUID
    ) -> Optional[SensorDataStatistics]:
        query = """
            SELECT
                unit_id,
                AVG(temperature) as avg_temperature,
                AVG(humidity) as avg_humidity,
                COUNT(*) as total_readings,
                COUNT(*) FILTER (
                    WHERE status = 'VALIDATED'
                ) as validated_readings,
                COUNT(*) FILTER (WHERE is_archived = true) as archived_readings
            FROM sensor_data
            WHERE unit_id = $1
            GROUP BY unit_id
        """
        result = await self.conn.fetchrow(query, unit_id)
        if not result:
            return None
        return SensorDataStatistics(**dict(result))

    async def archive_data(self, sensor_data_id: UUID) -> bool:
        query = """
            UPDATE sensor_data
            SET is_archived = true
            WHERE id = $1
        """
        result = await self.conn.execute(query, sensor_data_id)
        return result == "UPDATE 1"

from typing import List, Dict, Any
from uuid import UUID, uuid4
import asyncpg
from app.schemas.sensor_data import (
    SensorDataCreate,
    SensorDataUpdate
)


class SensorDataRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(self, data: SensorDataCreate) -> Dict[str, Any] | None:
        query = """
            INSERT INTO sensor_data
                (id, unit_id, temperature, humidity, status, is_archived)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *
        """
        record_id = uuid4()
        try:
            async with self.pool.acquire() as conn:
                record = await conn.fetchrow(
                    query,
                    record_id,
                    data.unit_id,
                    data.temperature,
                    data.humidity,
                    data.status,
                    data.is_archived
                )
                return dict(record) if record else None
        except asyncpg.exceptions.ForeignKeyViolationError:
            raise ValueError(f"Unit with id '{data.unit_id}' does not exist.")

    async def get_by_id(self, sensor_data_id: UUID) -> Dict[str, Any] | None:
        query = "SELECT * FROM sensor_data WHERE id = $1;"
        async with self.pool.acquire() as conn:
            record = await conn.fetchrow(query, sensor_data_id)
            return dict(record) if record else None

    async def get_all(
            self,
            limit: int = 100,
            offset: int = 0,
            unit_id: UUID | None = None
    ) -> List[Dict[str, Any]]:
        base_query = "SELECT * FROM sensor_data"
        where_clause = " WHERE unit_id = $3" if unit_id else ""
        order_clause = " ORDER BY timestamp DESC"
        limit_clause = " LIMIT $1 OFFSET $2"

        query = base_query + where_clause + order_clause + limit_clause

        async with self.pool.acquire() as conn:
            if unit_id:
                records = await conn.fetch(query, limit, offset, unit_id)
            else:
                records = await conn.fetch(
                    base_query + order_clause + limit_clause,
                    limit,
                    offset
                )
            return [dict(r) for r in records]

    async def get_by_unit(
            self,
            unit_id: UUID,
            limit: int = 100,
            offset: int = 0
    ) -> List[Dict[str, Any]]:
        query = """
            SELECT * FROM sensor_data
            WHERE unit_id = $1
            ORDER BY timestamp DESC
            LIMIT $2 OFFSET $3;
        """
        async with self.pool.acquire() as conn:
            records = await conn.fetch(query, unit_id, limit, offset)
            return [dict(r) for r in records]

    async def update(
            self,
            sensor_data_id: UUID,
            data: SensorDataUpdate
    ) -> Dict[str, Any] | None:
        updates = []
        values = []
        i = 1

        data_dict = data.model_dump(exclude_none=True)

        for field, value in data_dict.items():
            updates.append(f"{field} = ${i}")
            values.append(value)
            i += 1

        if not updates:
            return await self.get_by_id(sensor_data_id)

        query = f"""
            UPDATE sensor_data
            SET {', '.join(updates)}
            WHERE id = ${i}
            RETURNING *;
        """
        values.append(sensor_data_id)

        try:
            async with self.pool.acquire() as conn:
                record = await conn.fetchrow(query, *values)
                return dict(record) if record else None
        except asyncpg.exceptions.ForeignKeyViolationError:
            raise ValueError("Referenced unit does not exist.")

    async def delete(self, sensor_data_id: UUID) -> bool:
        query = "DELETE FROM sensor_data WHERE id = $1;"
        async with self.pool.acquire() as conn:
            status = await conn.execute(query, sensor_data_id)
            return status == 'DELETE 1'

    async def get_unit_statistics(
            self,
            unit_id: UUID
    ) -> Dict[str, Any] | None:
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
            GROUP BY unit_id;
        """
        async with self.pool.acquire() as conn:
            record = await conn.fetchrow(query, unit_id)
            if not record:
                return None
            return dict(record)

    async def archive_data(
            self,
            sensor_data_id: UUID
    ) -> Dict[str, Any] | None:
        query = """
            UPDATE sensor_data
            SET is_archived = true
            WHERE id = $1
            RETURNING *;
        """
        async with self.pool.acquire() as conn:
            record = await conn.fetchrow(query, sensor_data_id)
            return dict(record) if record else None

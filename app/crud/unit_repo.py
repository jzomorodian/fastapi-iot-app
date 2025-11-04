import asyncpg
from typing import List, Dict, Any
from uuid import UUID, uuid4
from app.schemas.unit import UnitCreate, UnitUpdate


class UnitRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(self, unit: UnitCreate) -> Dict[str, Any] | None:
        unit_id = uuid4()
        query = """
        INSERT INTO units (id, name, location, is_active)
        VALUES ($1, $2, $3, TRUE)
        RETURNING id, name, location, is_active, created_at;
        """
        try:
            async with self.pool.acquire() as conn:
                record = await conn.fetchrow(query, unit_id,
                                             unit.name, unit.location)
                return dict(record) if record else None
        except asyncpg.exceptions.UniqueViolationError:
            # Re-raise a custom exception if using ORM,
            # but here we let the API handle the HTTPException
            raise ValueError(f"Unit name '{unit.name}' already exists.")

    async def get_all(
            self,
            limit: int = 100,
            offset: int = 0
    ) -> List[Dict[str, Any]]:
        query = """
            SELECT * FROM units ORDER BY created_at DESC LIMIT $1 OFFSET $2;
        """
        async with self.pool.acquire() as conn:
            records = await conn.fetch(query, limit, offset)
            return [dict(r) for r in records]

    async def get_by_id(self, unit_id: UUID) -> Dict[str, Any] | None:
        query = "SELECT * FROM units WHERE id = $1;"
        async with self.pool.acquire() as conn:
            record = await conn.fetchrow(query, unit_id)
            return dict(record) if record else None

    async def update(
            self,
            unit_id: UUID,
            unit: UnitUpdate
    ) -> Dict[str, Any] | None:
        # Build the query dynamically for partial updates
        updates = []
        values = []
        i = 1  # Start index for $ placeholders

        data = unit.model_dump(exclude_none=True)

        if 'name' in data:
            updates.append(f"name = ${i}")
            values.append(data['name'])
            i += 1
        if 'location' in data:
            updates.append(f"location = ${i}")
            values.append(data['location'])
            i += 1
        if 'is_active' in data:
            updates.append(f"is_active = ${i}")
            values.append(data['is_active'])
            i += 1

        if not updates:
            # No changes, return current state
            return await self.get_by_id(unit_id)

        query = f"""
            UPDATE units SET {', '.join(updates)} WHERE id = ${i} RETURNING *;
            """
        values.append(unit_id)

        try:
            async with self.pool.acquire() as conn:
                record = await conn.fetchrow(query, *values)
                return dict(record) if record else None
        except asyncpg.exceptions.UniqueViolationError:
            raise ValueError("Unit name already exists.")

    async def delete(self, unit_id: UUID) -> bool:
        query = "DELETE FROM units WHERE id = $1;"
        async with self.pool.acquire() as conn:
            # execute() returns status, command (DELETE 1)
            status = await conn.execute(query, unit_id)
            # Check if one row was deleted
            return status == 'DELETE 1'

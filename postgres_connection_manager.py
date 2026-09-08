import logging
import psycopg
from psycopg_pool import AsyncConnectionPool

logger = logging.getLogger(__name__)

class PostgresConnectionManager:
    def __init__(self, connection_params: dict) -> None:
        self.connection_params = connection_params
        self.pool = None

    async def connect(self) -> None:
        self.pool = AsyncConnectionPool(kwargs=self.connection_params, min_size=2, max_size=5, open=False)
        await self.pool.open()

    async def execute_query(self, query: str, params: tuple | list = None, fetch: bool = False) -> list | None:
        try:
            async with self.pool.connection() as connection:
                async with connection.cursor() as cursor:
                    logger.debug("Executing query: %s | params: %s", query, params)
                    await cursor.execute(query, params)
                    if fetch:
                        result = await cursor.fetchall()
                        return result
                    return None
        except psycopg.DatabaseError as error:
            raise Exception(f"Query failed: {error}") from error

    async def execute_many(self, query: str, data: list[tuple]) -> None:
        try:
            async with self.pool.connection() as connection:
                async with connection.cursor() as cursor:
                    logger.debug("Executing query: %s | %d rows", query, len(data))
                    await cursor.executemany(query, data)
        except psycopg.DatabaseError as error:
            raise Exception(f"Query failed: {error}") from error

    async def close(self) -> None:
        if self.pool is not None:
           await self.pool.close()
import logging
import aiomysql
from db.database_connection_manager import DatabaseConnectionManager

logger = logging.getLogger(__name__)

class MySQLConnectionManager(DatabaseConnectionManager):
    def __init__(self, connection_params: dict) -> None:
        self.connection_params = connection_params
        self.pool = None

    async def connect(self) -> None:
        self.pool = await aiomysql.create_pool(minsize=2, maxsize=5, autocommit=False, **self.connection_params)

    async def execute_query(self, query: str, params: tuple | list = None, fetch: bool = False) -> list | None:
        async with self.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                try:
                    logger.debug("Executing query: %s | params: %s", query, params)
                    await cursor.execute(query, params)
                    result = await cursor.fetchall() if fetch else None
                    await connection.commit()
                    return result
                except Exception as error:
                    await connection.rollback()
                    raise Exception(f"Query failed: {error}") from error

    async def execute_many(self, query: str, data: list[tuple]) -> None:
        async with self.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                try:
                    logger.debug("Executing query: %s | %d rows", query, len(data))
                    await cursor.executemany(query, data)
                    await connection.commit()
                except Exception as error:
                    await connection.rollback()
                    raise Exception(f"Query failed: {error}") from error

    async def close(self) -> None:
        if self.pool is not None:
            self.pool.close()
            await self.pool.wait_closed()
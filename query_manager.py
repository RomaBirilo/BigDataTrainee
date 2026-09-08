from postgres_connection_manager import PostgresConnectionManager
import logging

logger = logging.getLogger(__name__)

class QueryManager:
    def __init__(self, connection_manager: PostgresConnectionManager) -> None:
        self.connection_manager = connection_manager

    async def rooms_with_students_number(self) -> list[dict]:
        query = """
            SELECT r.name, COUNT(s.id)
            FROM rooms AS r
            LEFT JOIN students AS s ON r.id = s.room
            GROUP BY r.id, r.name
            ORDER BY r.id;
        """

        logger.debug("Executing query: rooms_with_students_number")
        raw_data = await self.connection_manager.execute_query(query, fetch=True)
        logger.debug("Query returned %s rows", len(raw_data))
        return [{"room_name": row[0], "student_count": row[1]} for row in raw_data]

    async def rooms_with_smallest_avg_age(self) -> list[dict]:
        query = """
            SELECT r.name, 
            EXTRACT(YEAR FROM AVG(AGE(s.birthday::date)))::int AS avg_age
            FROM rooms AS r
            INNER JOIN students AS s ON r.id = s.room
            GROUP BY r.name
            ORDER BY avg_age
            LIMIT 5;
        """

        logger.debug("Executing query: rooms_with_smallest_avg_age")
        raw_data = await self.connection_manager.execute_query(query, fetch=True)
        logger.debug("Query returned %s rows", len(raw_data))
        return [{"room_name": row[0], "avg_age": row[1]} for row in raw_data]

    async def rooms_with_largest_age_diff(self) -> list[dict]:
        query = """
            SELECT r.name, 
            EXTRACT(YEAR FROM MAX(AGE(s.birthday::date)) - MIN(AGE(s.birthday::date)))::int AS age_diff
            FROM rooms AS r
            INNER JOIN students AS s ON r.id = s.room
            GROUP BY r.name
            ORDER BY age_diff DESC
            LIMIT 5;
        """

        logger.debug("Executing query: rooms_with_largest_age_diff")
        raw_data = await self.connection_manager.execute_query(query, fetch=True)
        logger.debug("Query returned %s rows", len(raw_data))
        return [{"room_name": row[0], "age_diff": row[1]} for row in raw_data]

    async def rooms_with_diff_sex_students(self) -> list[dict]:
        query = """
            SELECT r.name
            FROM rooms AS r
            INNER JOIN students AS s ON r.id = s.room
            GROUP BY r.id, r.name
            HAVING COUNT(DISTINCT s.sex) = 2
            ORDER BY r.id;     
        """

        logger.debug("Executing query: rooms_with_diff_sex_students")
        raw_data = await self.connection_manager.execute_query(query, fetch=True)
        logger.debug("Query returned %s rows", len(raw_data))
        return [{"room_name": row[0]} for row in raw_data]
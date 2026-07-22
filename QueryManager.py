from PostgresConnectionManager import PostgresConnectionManager

class QueryManager:
    def __init__(self, connection_manager: PostgresConnectionManager) -> None:
        self.connection_manager = connection_manager

    def rooms_with_students_number(self) -> list[dict]:
        query = """
            SELECT r.name, COUNT(s.id)
            FROM rooms AS r
            LEFT JOIN students AS s ON r.id = s.room
            GROUP BY r.id, r.name
            ORDER BY r.id;
        """
        try:
            raw_data = self.connection_manager.execute_query(query, fetch=True)
            return [{"room_name": row[0], "student_count": row[1]} for row in raw_data]
        except Exception as error:
            raise Exception(error)

    def rooms_with_smallest_avg_age(self):
        query = """
            SELECT r.name, 
            EXTRACT(YEAR FROM AVG(AGE(s.birthday::date)))::int AS avg_age
            FROM rooms AS r
            INNER JOIN students AS s ON r.id = s.room
            GROUP BY r.name
            ORDER BY avg_age
            LIMIT 5;
        """
        try:
            raw_data = self.connection_manager.execute_query(query, fetch=True)
            return [{"room_name": row[0], "avg_age": row[1]} for row in raw_data]
        except Exception as error:
            raise Exception(error)

    def rooms_with_largest_age_diff(self):
        query = """
            SELECT r.name, 
            EXTRACT(YEAR FROM MAX(AGE(s.birthday::date)) - MIN(AGE(s.birthday::date)))::int AS age_diff
            FROM rooms AS r
            INNER JOIN students AS s ON r.id = s.room
            GROUP BY r.name
            ORDER BY age_diff DESC
            LIMIT 5;
        """
        try:
            raw_data = self.connection_manager.execute_query(query, fetch=True)
            return [{"room_name": row[0], "age_diff": row[1]} for row in raw_data]
        except Exception as error:
            raise Exception(error)

    def rooms_with_diff_sex_students(self):
        query = """
            SELECT r.name
            FROM rooms AS r
            INNER JOIN students AS s ON r.id = s.room
            GROUP BY r.id, r.name
            HAVING COUNT(DISTINCT s.sex) = 2
            ORDER BY r.id;     
        """
        try:
            raw_data = self.connection_manager.execute_query(query, fetch=True)
            return [{"room_name": row[0]} for row in raw_data]
        except Exception as error:
            raise Exception(error)

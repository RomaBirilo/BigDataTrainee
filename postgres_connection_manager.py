import psycopg2

class PostgresConnectionManager:
    def __init__(self, connection_params: dict) -> None:
        self.connection_params = connection_params
        self.connection = None
        self.cursor = None

    def connect(self) -> None:
        self.connection = psycopg2.connect(**self.connection_params)
        self.cursor = self.connection.cursor()

    def execute_query(self, query: str, params: tuple | list = None, fetch: bool = False) -> list | None:
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            if fetch:
                result = self.cursor.fetchall()
                self.connection.commit()
                return result
            self.connection.commit()
            return None
        except psycopg2.DatabaseError as error:
            if self.connection:
                self.connection.rollback()
            raise Exception(f"Query failed: {error}")

    def close(self) -> None:
        if self.cursor is not None:
            self.cursor.close()
        if self.connection is not None:
            self.connection.close()
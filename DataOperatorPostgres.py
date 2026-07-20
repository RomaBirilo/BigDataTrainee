import psycopg2
import json

class DataOperatorPostgres:
    def __init__(self, connection_params: dict) -> None:
        self.connection_params = connection_params
        self.connection = None
        self.cursor = None
        self.response = None

    def connect(self) -> None:
        try:
            self.connection = psycopg2.connect(**self.connection_params)
            self.cursor = self.connection.cursor()
        except Exception as error:
            raise Exception(f"Connection failed: {error}")

    def close(self) -> None:
        if self.cursor is not None:
            self.cursor.close()
        if self.connection is not None:
            self.connection.close()

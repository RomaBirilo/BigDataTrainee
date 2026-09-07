from postgres_connection_manager import PostgresConnectionManager
from psycopg2 import extras
import psycopg2

class PostgresSchemaManager:
    def __init__(self, connection_manager: PostgresConnectionManager, type_mapping: dict = None) -> None:
        self.connection_manager = connection_manager
        if type_mapping:
            self.TYPE_MAPPING = type_mapping
        else:
            self.TYPE_MAPPING = {
                int: "INT",
                float: "REAL",
                str: "VARCHAR(255)",
                bool: "BOOLEAN"
            }

    def create_table(self, table_name: str, sample_data: dict, primary_key: str) -> None:
        columns_parts = []
        for key, value in sample_data.items():
            if key == primary_key and self.TYPE_MAPPING.get(type(value)) == "INT":
                columns_parts.append(f"{key} SERIAL PRIMARY KEY")
            elif key == primary_key:
                columns_parts.append(f"{key} " + self.TYPE_MAPPING.get(type(value), "TEXT") + " PRIMARY KEY")
            else:
                columns_parts.append(f"{key} " + self.TYPE_MAPPING.get(type(value), "TEXT"))
        columns = ','.join(columns_parts)
        query = f"CREATE TABLE IF NOT EXISTS {table_name}({columns});"
        try:
            self.connection_manager.execute_query(query)
        except Exception as error:
            raise Exception(f"Failed creating table: {error}")

    def insert_data(self, table_name: str, file_data: list) -> None:
        if not file_data:
            return
        fields_parts = list(file_data[0].keys())
        fields = ','.join(fields_parts)
        data_to_insert = [tuple(item[key] for key in fields_parts) for item in file_data]
        query = f"INSERT INTO {table_name} ({fields}) VALUES %s;"
        try:
            extras.execute_values(self.connection_manager.cursor, query, data_to_insert)
            self.connection_manager.connection.commit()
        except psycopg2.DatabaseError as error:
            raise Exception(f"Failed inserting data: {error}")

    def create_relationship(self, left_table_name: str, left_table_field:str,
                            right_table_name: str, right_table_field: str) -> None:
        query = f"""
            ALTER TABLE {left_table_name}
            ADD CONSTRAINT fk_{left_table_name}_{right_table_name}
            FOREIGN KEY ({left_table_field}) REFERENCES {right_table_name}({right_table_field})
            ON DELETE CASCADE; 
        """
        try:
            self.connection_manager.execute_query(query)
        except Exception as error:
            raise Exception(f"Failed creating relationship: {error}")

    def create_index(self, table_name: str, table_field: str) -> None:
        query = f"CREATE INDEX IF NOT EXISTS idx_{table_name}_{table_field} ON {table_name}({table_field})"
        try:
            self.connection_manager.execute_query(query)
        except Exception as error:
            raise Exception(f"Failed creating index: {error}")
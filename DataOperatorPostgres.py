import psycopg2
from psycopg2 import extras
import json

class DataOperatorPostgres:
    def __init__(self, connection_params: dict) -> None:
        self.connection_params = connection_params
        self.connection = None
        self.cursor = None
        self.file_data = None
        self.response = None
        self.TYPE_MAPPING = {
            int: "INT",
            float: "REAL",
            str: "VARCHAR(255)",
            bool: "BOOLEAN"
        }

    def connect(self) -> None:
        try:
            self.connection = psycopg2.connect(**self.connection_params)
            self.cursor = self.connection.cursor()
            print("Connection success!")
        except Exception as error:
            raise Exception(f"Connection failed: {error}")

    def read_json_file(self, path: str) -> None:
        try:
            with open(path, 'r') as file:
                self.file_data = json.load(file)
                print(f"File {path} was read successfully!")
        except FileNotFoundError:
            raise Exception(f"File {path} not found!")
        except json.JSONDecodeError as error:
            raise Exception(f"Incorrect json syntaxis! Line:{error.lineno}")
        except Exception:
            raise Exception("Unknown error!")

    def execute_query(self, query: str) -> None:
        try:
            self.cursor.execute(query)
            self.connection.commit()
        except psycopg2.DatabaseError as error:
            raise Exception(f"Query failed: {error}")

    def create_table(self, table_name: str, primary_key: str) -> None:
        columns_parts = []
        for key, value in self.file_data[0].items():
            if key == primary_key and self.TYPE_MAPPING.get(type(value)) == "INT":
                columns_parts.append(f"{key} SERIAL PRIMARY KEY")
            elif key == primary_key:
                columns_parts.append(f"{key} " + self.TYPE_MAPPING.get(type(value), "TEXT") + " PRIMARY KEY")
            else:
                columns_parts.append(f"{key} " + self.TYPE_MAPPING.get(type(value), "TEXT"))
        columns = ','.join(columns_parts)
        query = f"CREATE TABLE IF NOT EXISTS {table_name}({columns});"
        print(query)
        try:
            self.execute_query(query)
            print("Your table was created successfully!")
        except Exception as error:
            raise Exception(f"Failed creating table: {error}")

    def insert_data(self, table_name: str) -> None:
        fields_parts = list(self.file_data[0].keys())
        fields = ','.join(fields_parts)
        data_to_insert = [tuple(item[key] for key in fields_parts) for item in self.file_data]
        query = f"INSERT INTO {table_name} " + '(' + fields + ')' + " VALUES %s;"
        try:
            extras.execute_values(self.cursor, query, data_to_insert)
            self.connection.commit()
            print("Your data was inserted successfully!")
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
            self.execute_query(query)
            print("Relationship was created successfully!")
        except Exception as error:
            raise Exception(f"Failed creating relationship: {error}")

    def close(self) -> None:
        if self.cursor is not None:
            self.cursor.close()
        if self.connection is not None:
            self.connection.close()

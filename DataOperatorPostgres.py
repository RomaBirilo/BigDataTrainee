import psycopg2
import json

class DataOperatorPostgres:
    def __init__(self, connection_params: dict) -> None:
        self.connection_params = connection_params
        self.connection = None
        self.cursor = None
        self.json_data = None
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
                self.json_data = json.load(file)
                print(f"File {path} was read successfully!")
        except FileNotFoundError:
            raise Exception(f"File {path} not found!")
        except json.JSONDecodeError as error:
            raise Exception(f"Incorrect json syntaxis! Line:{error.lineno}")
        except Exception:
            raise Exception("Unknown error!")

    def create_table(self, table_name: str, primary_key: str) -> None:
        columns_parts = []
        for key, value in self.json_data[0].items():
            if key == primary_key and self.TYPE_MAPPING.get(type(value)) == "INT":
                columns_parts.append(f"{key} SERIAL PRIMARY KEY")
            elif key == primary_key:
                columns_parts.append(f"{key} " + self.TYPE_MAPPING.get(type(value), "TEXT") + " PRIMARY KEY")
            else:
                columns_parts.append(f"{key} " + self.TYPE_MAPPING.get(type(value), "TEXT"))
        columns = ','.join(columns_parts)
        print(f"CREATE TABLE IF NOT EXISTS {table_name}({columns});")
        try:
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name}({columns});")
            self.connection.commit()
        except psycopg2.DatabaseError as error:
            raise Exception(f"Failed creating table: {error}")

    def close(self) -> None:
        if self.cursor is not None:
            self.cursor.close()
        if self.connection is not None:
            self.connection.close()

import logging
from dotenv import load_dotenv
import os

from json_file_manager import JSONFileManager
from postgres_connection_manager import PostgresConnectionManager
from postgres_schema_manager import PostgresSchemaManager
from query_manager import QueryManager

load_dotenv()

conn_params = {
    "host": os.getenv("HOST"),
    "database": os.getenv("DATABASE"),
    "user": os.getenv("USER"),
    "password": os.getenv("PASSWORD"),
    "port": os.getenv("PORT")
}

def main(connection_params: dict) -> None:
    db_connection = PostgresConnectionManager(connection_params)
    try:
        print("Try to connect...")
        db_connection.connect()
        print("Connection successfully!")

        print("Reading files...")
        rooms_data = JSONFileManager.read_json_file("rooms.json")
        students_data = JSONFileManager.read_json_file("students.json")
        print("Files were read successfully!")

        schema_manager = PostgresSchemaManager(connection_manager=db_connection)

        print("Creating schema...")
        schema_manager.create_table("rooms", rooms_data[0], "id")
        print("Table was created successfully!")
        schema_manager.insert_data("rooms", rooms_data)
        print("Data was inserted successfully!")

        schema_manager.create_table("students", students_data[0], "id")
        print("Table was created successfully!")
        schema_manager.insert_data("students", students_data)
        print("Data was inserted successfully!")

        schema_manager.create_relationship("students", "room",
                                           "rooms", "id")
        print("Relationship was created successfully!")

        schema_manager.create_index("rooms", "name")
        print("Index was created successfully!")
        schema_manager.create_index("students", "name")
        print("Index was created successfully!")
        schema_manager.create_index("students", "birthday")
        print("Index was created successfully!")
        print("Schema was created successfully!")

        query_manager = QueryManager(connection_manager=db_connection)

        print("Queries execution...")
        response = query_manager.rooms_with_students_number()
        JSONFileManager.write_json_file("rooms_with_students_number.json", response)

        response = query_manager.rooms_with_smallest_avg_age()
        JSONFileManager.write_json_file("rooms_with_smallest_avg_age.json", response)

        response = query_manager.rooms_with_largest_age_diff()
        JSONFileManager.write_json_file("rooms_with_largest_age_diff.json", response)

        response = query_manager.rooms_with_diff_sex_students()
        JSONFileManager.write_json_file("rooms_with_diff_sex_students.json", response)
        print("All queries were executed successfully!")

    except Exception as error:
        print(error)
    finally:
        db_connection.close()

if __name__ == "__main__":
    main(connection_params=conn_params)
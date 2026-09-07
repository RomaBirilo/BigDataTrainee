from dotenv import load_dotenv
load_dotenv()

from logging_config import setup_logging
setup_logging()

import logging
import os
import sys

from json_file_manager import JSONFileManager
from postgres_connection_manager import PostgresConnectionManager
from postgres_schema_manager import PostgresSchemaManager
from query_manager import QueryManager

logger = logging.getLogger(__name__)

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
        logger.info("Connecting to database...")
        db_connection.connect()
        logger.info("Connection successfully")

        logger.info("Reading input files...")
        rooms_data = JSONFileManager.read_json_file("rooms.json")
        students_data = JSONFileManager.read_json_file("students.json")
        logger.info("Files read successfully")

        logger.info("Starting schema creation")
        schema_manager = PostgresSchemaManager(connection_manager=db_connection)

        schema_manager.create_table("rooms", rooms_data[0], "id")
        schema_manager.insert_data("rooms", rooms_data)

        schema_manager.create_table("students", students_data[0], "id")
        schema_manager.insert_data("students", students_data)

        schema_manager.create_relationship("students", "room",
                                           "rooms", "id")

        schema_manager.create_index("rooms", "name")
        schema_manager.create_index("students", "name")
        schema_manager.create_index("students", "birthday")
        logger.info("Schema creation completed")

        logger.info("Executing queries...")
        query_manager = QueryManager(connection_manager=db_connection)

        response = query_manager.rooms_with_students_number()
        JSONFileManager.write_json_file("rooms_with_students_number.json", response)

        response = query_manager.rooms_with_smallest_avg_age()
        JSONFileManager.write_json_file("rooms_with_smallest_avg_age.json", response)

        response = query_manager.rooms_with_largest_age_diff()
        JSONFileManager.write_json_file("rooms_with_largest_age_diff.json", response)

        response = query_manager.rooms_with_diff_sex_students()
        JSONFileManager.write_json_file("rooms_with_diff_sex_students.json", response)
        logger.info("All queries executed successfully")

    except Exception as error:
        logger.exception("Unhandled error during script execution")
        sys.exit(1)
    finally:
        db_connection.close()

if __name__ == "__main__":
    main(connection_params=conn_params)
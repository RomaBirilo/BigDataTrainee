from dotenv import load_dotenv
load_dotenv()

from logging_config import setup_logging
setup_logging()

import logging
import asyncio
import sys

from json_file_manager import JSONFileManager
from postgres_connection_manager import PostgresConnectionManager
from postgres_schema_manager import PostgresSchemaManager
from query_manager import QueryManager
from config_settings import PGSettings

logger = logging.getLogger(__name__)

config = PGSettings()
conn_params = {
    "host": config.host,
    "dbname": config.pg_database,
    "user": config.pg_user,
    "password": config.pg_password,
    "port": config.pg_port
}

async def main(connection_params: dict) -> None:
    db_connection = PostgresConnectionManager(connection_params)
    try:
        logger.info("Connecting to database...")
        await db_connection.connect()
        logger.info("Connection successfully")

        logger.info("Reading input files...")
        rooms_data = JSONFileManager.read_json_file("rooms.json")
        students_data = JSONFileManager.read_json_file("students.json")
        logger.info("Files read successfully")

        logger.info("Starting schema creation")
        schema_manager = PostgresSchemaManager(connection_manager=db_connection)

        await schema_manager.create_table("rooms", rooms_data[0], "id")
        await schema_manager.insert_data("rooms", rooms_data)

        await schema_manager.create_table("students", students_data[0], "id")
        await schema_manager.insert_data("students", students_data)

        await schema_manager.create_relationship("students", "room",
                                           "rooms", "id")

        await schema_manager.create_index("rooms", "name")
        await schema_manager.create_index("students", "name")
        await schema_manager.create_index("students", "birthday")
        logger.info("Schema creation completed")

        logger.info("Executing queries...")
        query_manager = QueryManager(connection_manager=db_connection)

        result = await asyncio.gather(query_manager.rooms_with_students_number(),
                                      query_manager.rooms_with_smallest_avg_age(),
                                      query_manager.rooms_with_largest_age_diff(),
                                      query_manager.rooms_with_diff_sex_students()
                                      )
        JSONFileManager.write_json_file("rooms_with_students_number.json", result[0])
        JSONFileManager.write_json_file("rooms_with_smallest_avg_age.json", result[1])
        JSONFileManager.write_json_file("rooms_with_largest_age_diff.json", result[2])
        JSONFileManager.write_json_file("rooms_with_diff_sex_students.json", result[3])
        logger.info("All queries executed successfully")

    except Exception:
        logger.exception("Unhandled error during script execution")
        sys.exit(1)
    finally:
        await db_connection.close()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main(connection_params=conn_params))
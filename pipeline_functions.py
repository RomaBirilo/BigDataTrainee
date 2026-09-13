from json_file_manager import JSONFileManager
from postgres_connection_manager import PostgresConnectionManager
from postgres_schema_manager import PostgresSchemaManager
from query_manager import QueryManager
import logging
import asyncio

logger = logging.getLogger(__name__)

async def connect_to_database(connection_params: dict) -> PostgresConnectionManager:
    db_connection = PostgresConnectionManager(connection_params)
    logger.info("Connecting to database...")
    await db_connection.connect()
    logger.info("Connection successfully")
    return db_connection

def load_input_data() -> tuple[list,list]:
    logger.info("Reading input files...")
    rooms_data = JSONFileManager.read_json_file("rooms.json")
    students_data = JSONFileManager.read_json_file("students.json")
    logger.info("Files read successfully")
    return rooms_data, students_data

async def create_database_schema(db_connection: PostgresConnectionManager, rooms_data: list, students_data: list) -> None:
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

async def run_queries(db_connection: PostgresConnectionManager) -> tuple[list, list, list, list]:
    logger.info("Executing queries...")
    query_manager = QueryManager(connection_manager=db_connection)

    result = await asyncio.gather(query_manager.rooms_with_students_number(),
                                  query_manager.rooms_with_smallest_avg_age(),
                                  query_manager.rooms_with_largest_age_diff(),
                                  query_manager.rooms_with_diff_sex_students()
                                  )
    logger.info("All queries executed successfully")
    return result

def save_results(result: tuple) -> None:
    logger.info("Writing output files...")
    JSONFileManager.write_json_file("rooms_with_students_number.json", result[0])
    JSONFileManager.write_json_file("rooms_with_smallest_avg_age.json", result[1])
    JSONFileManager.write_json_file("rooms_with_largest_age_diff.json", result[2])
    JSONFileManager.write_json_file("rooms_with_diff_sex_students.json", result[3])
    logger.info("Results saved successfully")
from database_connection_manager import DatabaseConnectionManager
from json_file_manager import JSONFileManager
from schema_manager import SchemaManager
from query_manager import QueryManager
import logging
import asyncio

from sql_dialect import SQLDialect

logger = logging.getLogger(__name__)

async def connect_to_database(db_connection: DatabaseConnectionManager) -> None:
    logger.info("Connecting to database...")
    await db_connection.connect()
    logger.info("Connection successfully")


def load_input_data() -> tuple[list,list]:
    logger.info("Reading input files...")
    rooms_data = JSONFileManager.read_json_file("rooms.json")
    students_data = JSONFileManager.read_json_file("students.json")
    logger.info("Files read successfully")
    return rooms_data, students_data

async def create_database_schema(db_connection: DatabaseConnectionManager, dialect: SQLDialect, rooms_data: list, students_data: list) -> None:
    logger.info("Starting schema creation")
    schema_manager = SchemaManager(connection_manager=db_connection, dialect=dialect)

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

async def run_queries(db_connection: DatabaseConnectionManager, dialect: SQLDialect) -> tuple[list, list, list, list]:
    logger.info("Executing queries...")
    query_manager = QueryManager(connection_manager=db_connection, dialect=dialect)

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
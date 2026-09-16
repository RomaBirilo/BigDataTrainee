from db.database_connection_manager import DatabaseConnectionManager
from data_sources.source_manager import SourceManager
from db.schema_manager import SchemaManager
from db.query_manager import QueryManager
import logging
import asyncio

from db.dialects.sql_dialect import SQLDialect

logger = logging.getLogger(__name__)

async def connect_to_database(db_connection: DatabaseConnectionManager) -> None:
    logger.info("Connecting to database...")
    await db_connection.connect()
    logger.info("Connection successfully")


async def load_input_data(src_manager: SourceManager) -> tuple[list,list]:
    logger.info("Reading input files...")
    rooms_data = await src_manager.read("rooms.json")
    students_data = await src_manager.read("students.json")
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

async def save_results(src_manager: SourceManager, result: tuple) -> None:
    logger.info("Writing output files...")
    await src_manager.write("rooms_with_students_number.json", result[0])
    await src_manager.write("rooms_with_smallest_avg_age.json", result[1])
    await src_manager.write("rooms_with_largest_age_diff.json", result[2])
    await src_manager.write("rooms_with_diff_sex_students.json", result[3])
    logger.info("Results saved successfully")
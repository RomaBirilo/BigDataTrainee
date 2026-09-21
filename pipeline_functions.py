from db.database_connection_manager import DatabaseConnectionManager
from data_sources.source_manager import SourceManager
from db.schema_manager import SchemaManager
from db.query_manager import QueryManager
from db.db_schema_settings import DBSchemaConfig
import logging
import asyncio

from db.dialects.sql_dialect import SQLDialect

logger = logging.getLogger(__name__)

async def connect_to_database(db_connection: DatabaseConnectionManager) -> None:
    logger.info("Connecting to database...")
    await db_connection.connect()
    logger.info("Connection successfully")

async def load_db_schema(src_manager: SourceManager, db_schema_path: str) -> DBSchemaConfig:
    logger.info("Reading db schema config file...")
    db_schema = DBSchemaConfig(**await src_manager.read(db_schema_path))
    logger.info("Schema config file read successfully")
    return db_schema

async def load_input_data(src_manager: SourceManager, db_schema: DBSchemaConfig) -> dict[str, list]:
    logger.info("Reading input files...")
    data_by_table = {}
    for table in db_schema.tables:
        data_by_table[table.name] = await src_manager.read(f"{table.name}.json")
    logger.info("Files read successfully")
    return data_by_table

async def create_database_schema(db_connection: DatabaseConnectionManager, dialect: SQLDialect, db_schema: DBSchemaConfig, data: dict[str, list]) -> None:
    logger.info("Starting schema creation")
    schema_manager = SchemaManager(connection_manager=db_connection, dialect=dialect)

    for table in db_schema.tables:
        table_data = data[table.name]
        await schema_manager.create_table(table.name, table_data[0], table.primary_key)
        await schema_manager.insert_data(table.name, table_data)

    for relationship in db_schema.relationships:
        await schema_manager.create_relationship(relationship.left_table, relationship.left_field,
                                             relationship.right_table, relationship.right_field)

    for index in db_schema.indexes:
        await schema_manager.create_index(index.table, index.field)
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
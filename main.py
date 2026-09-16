from dotenv import load_dotenv
load_dotenv()

from logging_config import setup_logging
setup_logging()

import logging
import asyncio
import sys

from factory import create_connection_manager, create_dialect, create_data_source
from pipeline_functions import (connect_to_database, load_input_data,
                                create_database_schema, run_queries, save_results)
from config_settings import AppSettings, DataSourceSettings

logger = logging.getLogger(__name__)

config = AppSettings()
conn_params = config.get_connection_params()

data_source_settings = DataSourceSettings()

async def main(connection_params: dict) -> None:
    db_connection = create_connection_manager(config.db_type, connection_params)
    dialect = create_dialect(config.db_type)
    input_source = create_data_source(**data_source_settings.get_input_source_kwargs())
    output_source = create_data_source(**data_source_settings.get_output_source_kwargs())
    try:
        await connect_to_database(db_connection)

        rooms_data, students_data = await load_input_data(input_source)

        await create_database_schema(db_connection, dialect, rooms_data, students_data)

        result = await run_queries(db_connection, dialect)

        await save_results(output_source, result)
    except Exception:
        logger.exception("Unhandled error during script execution")
        sys.exit(1)
    finally:
        await db_connection.close()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main(connection_params=conn_params))
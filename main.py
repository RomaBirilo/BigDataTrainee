from dotenv import load_dotenv
load_dotenv()

from logging_config import setup_logging
setup_logging()

import logging
import asyncio
import sys

from factory import create_connection_manager, create_dialect
from pipeline_functions import (connect_to_database, load_input_data,
                                create_database_schema, run_queries, save_results)
from config_settings import AppSettings

logger = logging.getLogger(__name__)

config = AppSettings()
conn_params = config.get_connection_params()

async def main(connection_params: dict) -> None:
    db_connection = create_connection_manager(config.db_type, connection_params)
    dialect = create_dialect(config.db_type)
    try:
        await connect_to_database(db_connection)

        rooms_data, students_data = load_input_data()

        await create_database_schema(db_connection, dialect, rooms_data, students_data)

        result = await run_queries(db_connection, dialect)

        save_results(result)
    except Exception:
        logger.exception("Unhandled error during script execution")
        sys.exit(1)
    finally:
        await db_connection.close()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main(connection_params=conn_params))
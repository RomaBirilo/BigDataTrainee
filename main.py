from dotenv import load_dotenv
load_dotenv()

from logging_config import setup_logging
setup_logging()

import logging
import asyncio
import sys

from pipeline_functions import (connect_to_database, load_input_data,
                                create_database_schema, run_queries, save_results)
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
    db_connection = None
    try:
        db_connection = await connect_to_database(connection_params)

        rooms_data, students_data = load_input_data()

        await create_database_schema(db_connection, rooms_data, students_data)

        result = await run_queries(db_connection)

        save_results(result)
    except Exception:
        logger.exception("Unhandled error during script execution")
        sys.exit(1)
    finally:
        if db_connection:
            await db_connection.close()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main(connection_params=conn_params))
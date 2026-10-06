from pendulum import datetime
from airflow.sdk import dag, task
import asyncio

@dag(
    schedule=None,
    start_date=datetime(2025, 1, 1),
    tags=['rooms_students_pipeline'],
    catchup=False
)
def rooms_students_pipeline():
    @task
    def load_config_task() -> dict:
        from config_settings import AppSettings

        config = AppSettings()
        return {
            "db_type": config.db_type,
            "conn_params": config.get_connection_params(),
        }

    @task
    def stream_load_task(cfg: dict) -> None:
        from logging_config import setup_logging
        setup_logging()

        from config_settings import DataSourceSettings
        from factory import create_connection_manager, create_dialect, create_data_source
        from data_sources.json_file_manager import JSONFileManager
        from pipeline_functions import connect_to_database, load_db_schema, create_database_schema

        data_source_settings = DataSourceSettings()
        from config_settings import AppSettings
        db_schema_path = AppSettings().db_schema_path

        async def run():
            db_connection = create_connection_manager(cfg["db_type"], cfg["conn_params"])
            dialect = create_dialect(cfg["db_type"])
            input_source = create_data_source(**data_source_settings.get_input_source_kwargs())
            db_schema_source = JSONFileManager()
            try:
                await connect_to_database(db_connection)
                db_schema = await load_db_schema(db_schema_source, db_schema_path)
                await create_database_schema(db_connection, dialect, input_source, db_schema)
            finally:
                await db_connection.close()

        asyncio.run(run())

    @task
    def run_queries_task(cfg: dict) -> tuple[list, list, list, list]:
        from logging_config import setup_logging
        setup_logging()

        from factory import create_connection_manager, create_dialect
        from pipeline_functions import connect_to_database, run_queries

        async def run():
            db_connection = create_connection_manager(cfg["db_type"], cfg["conn_params"])
            dialect = create_dialect(cfg["db_type"])
            try:
                await connect_to_database(db_connection)
                return await run_queries(db_connection, dialect)
            finally:
                await db_connection.close()

        return asyncio.run(run())

    @task
    def save_results_task(result: tuple[list, list, list, list]) -> None:
        from logging_config import setup_logging
        setup_logging()

        from config_settings import DataSourceSettings
        from factory import create_data_source
        from pipeline_functions import save_results

        data_source_settings = DataSourceSettings()
        output_source = create_data_source(**data_source_settings.get_output_source_kwargs())
        asyncio.run(save_results(output_source, result))

    cfg = load_config_task()
    load_task = stream_load_task(cfg)
    query_task = run_queries_task(cfg)

    load_task >> query_task
    save_results_task(query_task)

rooms_students_pipeline()
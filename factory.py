from database_connection_manager import DatabaseConnectionManager
from postgres_connection_manager import PostgresConnectionManager
from sql_dialect import SQLDialect
from postgres_dialect import PostgresDialect

def create_connection_manager(db_type: str, connection_params: dict) -> DatabaseConnectionManager:
    if db_type == "postgres":
        db_connection = PostgresConnectionManager(connection_params)
    elif db_type == "mysql":
        db_connection = None
    else:
        raise ValueError(f"Unknown database type: {db_type}")
    return db_connection

def create_dialect(db_type: str) -> SQLDialect:
    if db_type == "postgres":
        dialect = PostgresDialect()
    elif db_type == "mysql":
        dialect = None
    else:
        raise ValueError(f"Unknown database type: {db_type}")
    return dialect

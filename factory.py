from database_connection_manager import DatabaseConnectionManager
from googledrive_file_manager import GoogleDriveFileManager
from json_file_manager import JSONFileManager
from mysql_connection_manager import MySQLConnectionManager
from postgres_connection_manager import PostgresConnectionManager
from source_manager import SourceManager
from sql_dialect import SQLDialect
from postgres_dialect import PostgresDialect
from mysql_dialect import MySQLDialect

def create_connection_manager(db_type: str, connection_params: dict) -> DatabaseConnectionManager:
    if db_type == "postgres":
        db_connection = PostgresConnectionManager(connection_params)
    elif db_type == "mysql":
        db_connection = MySQLConnectionManager(connection_params)
    else:
        raise ValueError(f"Unknown database type: {db_type}")
    return db_connection

def create_dialect(db_type: str) -> SQLDialect:
    if db_type == "postgres":
        dialect = PostgresDialect()
    elif db_type == "mysql":
        dialect = MySQLDialect()
    else:
        raise ValueError(f"Unknown database type: {db_type}")
    return dialect

def create_data_source(source_type: str,
    client_secret_path: str | None = None,
    token_path: str | None = None,
    folder_id: str | None = None
) -> SourceManager:
    if source_type == "local_drive":
        src_manager = JSONFileManager()
    elif source_type == "google_drive":
        src_manager = GoogleDriveFileManager(client_secret_path=client_secret_path,
            token_path=token_path,
            folder_id=folder_id)
    else:
        raise ValueError(f"Unknown data source type: {source_type}")
    return src_manager

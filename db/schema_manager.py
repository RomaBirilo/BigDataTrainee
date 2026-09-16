from db.database_connection_manager import DatabaseConnectionManager
from db.dialects.sql_dialect import SQLDialect
import logging

logger = logging.getLogger(__name__)

class SchemaManager:
    def __init__(self, connection_manager: DatabaseConnectionManager, dialect: SQLDialect) -> None:
        self.connection_manager = connection_manager
        self.dialect = dialect

    async def create_table(self, table_name: str, sample_data: dict, primary_key: str) -> None:
        columns_parts = []
        for key, value in sample_data.items():
            if key == primary_key:
                columns_parts.append(self.dialect.primary_key_column(key, type(value)))
            else:
                columns_parts.append(f"{key} {self.dialect.column_type(type(value))}")
        columns = ','.join(columns_parts)

        query = f"CREATE TABLE IF NOT EXISTS {table_name}({columns});"

        logger.debug("Creating table %s", table_name)
        await self.connection_manager.execute_query(query)

    async def insert_data(self, table_name: str, file_data: list) -> None:
        if not file_data:
            return

        fields_parts = list(file_data[0].keys())
        fields = ','.join(fields_parts)
        placeholders = ','.join(['%s'] * len(fields_parts))
        data_to_insert = [tuple(item[key] for key in fields_parts) for item in file_data]

        query = f"INSERT INTO {table_name} ({fields}) VALUES ({placeholders});"

        logger.debug("Inserting data to %s table", table_name)
        await self.connection_manager.execute_many(query, data_to_insert)
        logger.debug("Inserted %d rows into %s", len(file_data), table_name)

    async def create_relationship(self, left_table_name: str, left_table_field:str,
                            right_table_name: str, right_table_field: str) -> None:
        query = f"""
            ALTER TABLE {left_table_name}
            ADD CONSTRAINT fk_{left_table_name}_{right_table_name}
            FOREIGN KEY ({left_table_field}) REFERENCES {right_table_name}({right_table_field})
            ON DELETE CASCADE; 
        """

        logger.debug("Creating relationship between %s and %s", left_table_name, right_table_name)
        await self.connection_manager.execute_query(query)

    async def create_index(self, table_name: str, table_field: str) -> None:
        query = f"CREATE INDEX idx_{table_name}_{table_field} ON {table_name}({table_field})"

        logger.debug("Creating index idx_%s_%s on %s(%s)", table_name, table_field, table_name, table_field)
        await self.connection_manager.execute_query(query)
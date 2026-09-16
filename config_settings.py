from pydantic_settings import BaseSettings

class PostgresSettings(BaseSettings):
    host: str = "localhost"
    database: str
    user: str
    password: str
    port: str

    class Config:
        env_prefix = "POSTGRES_"

class MySQLSettings(BaseSettings):
    host: str = "localhost"
    database: str
    user: str
    password: str
    port: str

    class Config:
        env_prefix = "MYSQL_"

class AppSettings(BaseSettings):
    db_type: str = "postgres"

    def get_connection_params(self) -> dict:
        if self.db_type == "postgres":
            settings = PostgresSettings()
            return {
                "host": settings.host,
                "dbname": settings.database,
                "user": settings.user,
                "password": settings.password,
                "port": settings.port,
            }
        elif self.db_type == "mysql":
            settings = MySQLSettings()
            return {
                "host": settings.host,
                "db": settings.database,
                "user": settings.user,
                "password": settings.password,
                "port": int(settings.port),
            }
        else:
            raise ValueError(f"Unsupported db_type: {self.db_type}")

class DataSourceSettings(BaseSettings):
    input_type: str = "local_drive"
    input_client_secret_path: str = ""
    input_token_path: str = "token_input.pickle"
    input_folder_id: str = ""

    output_type: str = "local_drive"
    output_client_secret_path: str = ""
    output_token_path: str = "token_output.pickle"
    output_folder_id: str = ""

    class Config:
        env_prefix = "DATA_SOURCE_"

    def get_input_source_kwargs(self) -> dict:
        return {
            "source_type": self.input_type,
            "client_secret_path": self.input_client_secret_path or None,
            "token_path": self.input_token_path,
            "folder_id": self.input_folder_id or None,
        }

    def get_output_source_kwargs(self) -> dict:
        return {
            "source_type": self.output_type,
            "client_secret_path": self.output_client_secret_path or None,
            "token_path": self.output_token_path,
            "folder_id": self.output_folder_id or None,
        }
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
                "database": settings.database,
                "user": settings.user,
                "password": settings.password,
                "port": settings.port,
            }
        else:
            raise ValueError(f"Unsupported db_type: {self.db_type}")
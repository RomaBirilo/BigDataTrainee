from pydantic_settings import BaseSettings

class PGSettings(BaseSettings):
    host: str
    pg_database: str
    pg_user: str
    pg_password: str
    pg_port: str
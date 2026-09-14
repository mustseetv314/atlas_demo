from functools import lru_cache
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Atlas"
    app_env: str = "production"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_version: str = "1.0.0"
    db_server: str = "sqlserver.internal.company"
    db_port: int = 1433
    db_name: str = "AtlasDb"
    db_username: str = "atlas_app"
    db_password: str = "change-me"
    db_driver: str = "ODBC Driver 18 for SQL Server"
    db_trust_server_certificate: str = "yes"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def database_url(self) -> str:
        connection = (
            f"DRIVER={{{self.db_driver}}};SERVER={self.db_server},{self.db_port};"
            f"DATABASE={self.db_name};UID={self.db_username};PWD={self.db_password};"
            f"Encrypt=yes;TrustServerCertificate={self.db_trust_server_certificate};"
        )
        return f"mssql+pyodbc:///?odbc_connect={quote_plus(connection)}"


@lru_cache
def get_settings() -> Settings:
    return Settings()

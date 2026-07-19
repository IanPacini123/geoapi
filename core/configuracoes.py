from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Localidade API"
    VERSION: str = "1.0.0"
    
    # Configuracao de banco de dados
    POSTGRES_USER: str = "admin"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "localidade"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    REDIS_URL: str = "redis://localhost:6379/0"
    ALLOWED_ORIGINS: str = ""
    RATE_LIMIT_GLOBAL: str = "100/minute"
    RATE_LIMIT_CEP: str = "30/minute"
    RATE_LIMIT_OPTIONS: str = "300/minute"
    
    @property
    def database_url(self) -> str:
        return f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

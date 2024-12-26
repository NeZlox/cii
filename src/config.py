from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MODE: Literal["DEV", "TEST", "PROD"]
    LOG_LEVEL: str

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    ELASTIC_HOST: str
    ELASTIC_PORT: int
    ELASTIC_INDEX: str

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def ELASTIC_URL(self):
        return f"http://{self.ELASTIC_HOST}:{self.ELASTIC_PORT}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
# settings.post_settings()

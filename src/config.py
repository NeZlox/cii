from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MODE: Literal["DEV", "TEST", "PROD"]
    LOG_LEVEL: str


    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
#settings.post_settings()

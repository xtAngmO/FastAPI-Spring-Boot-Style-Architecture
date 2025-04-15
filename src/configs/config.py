from functools import lru_cache
from typing import Literal, Self

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "FastAPI App"
    DEBUG: bool = True
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "test"
    JWT_PRIVATE_KEY_PATH: str = "private.pem"
    JWT_PUBLIC_KEY_PATH: str = "public.pem"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    PORT: int = 8080
    CORS_ORIGINS: str = "http://localhost:3000"
    API_PREFIX: str = "/api"
    ENVIRONMENT: Literal["developer", "production"] = "developer"

    model_config = SettingsConfigDict(env_file=".env")

    @computed_field
    def JWT_PRIVATE_KEY(self: Self) -> str:  # noqa: N802
        try:
            with open(self.JWT_PRIVATE_KEY_PATH) as f:
                return f.read()
        except FileNotFoundError:
            return ""

    @computed_field
    def JWT_PUBLIC_KEY(self: Self) -> str:  # noqa: N802
        try:
            with open(self.JWT_PUBLIC_KEY_PATH) as f:
                return f.read()
        except FileNotFoundError:
            return ""


@lru_cache
def get_settings() -> Settings:
    return Settings()

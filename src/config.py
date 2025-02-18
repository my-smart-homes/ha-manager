from typing import Any

from pydantic import PostgresDsn, RedisDsn, model_validator, field_validator
from pydantic_settings import BaseSettings

from src.constants import Environment
import json


class Config(BaseSettings):
    DATABASE_URL: PostgresDsn
    REDIS_URL: RedisDsn

    SITE_DOMAIN: str = "myapp.com"

    ENVIRONMENT: Environment = Environment.PRODUCTION

    SENTRY_DSN: str | None = None

    CORS_ORIGINS: list[str] | str
    CORS_ORIGINS_REGEX: str | None = None
    CORS_HEADERS: list[str] | str
    APP_VERSION: str = "1.0.0"
    ECHO_SQL: bool = False

    @model_validator(mode="after")
    def validate_sentry_non_local(self) -> "Config":
        if self.ENVIRONMENT.is_deployed and not self.SENTRY_DSN:
            raise ValueError("Sentry is not set")

        return self

    @field_validator('CORS_ORIGINS', 'CORS_HEADERS', mode="before")
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [x.strip() for x in value.split(',')]
        return value

    class Config:
        env_file = '.env'
        extra = 'ignore'


settings = Config()

app_configs: dict[str, Any] = {
    "title": "Example Project API",
    "version": settings.APP_VERSION
}

if settings.ENVIRONMENT.is_deployed:
    app_configs["root_path"] = f"/v{settings.APP_VERSION}"

if not settings.ENVIRONMENT.is_debug:
    app_configs["openapi_url"] = None  # hide docs

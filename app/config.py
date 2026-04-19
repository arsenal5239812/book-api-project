import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")


def _get_env(key: str, default: str) -> str:
    return os.getenv(key, default)


@dataclass(frozen=True)
class Settings:
    app_title: str
    app_description: str
    app_version: str
    healthcheck_message: str
    openapi_url: str
    docs_url: str
    redoc_url: str
    redoc_js_url: str
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int


settings = Settings(
    app_title=_get_env("APP_TITLE", "Book Metadata and Recommendation API"),
    app_description=_get_env(
        "APP_DESCRIPTION",
        "A production-style coursework API with CRUD, authentication, analytics, and SQL persistence.",
    ),
    app_version=_get_env("APP_VERSION", "1.0.0"),
    healthcheck_message=_get_env(
        "HEALTHCHECK_MESSAGE",
        "Book Metadata and Recommendation API is running",
    ),
    openapi_url=_get_env("OPENAPI_URL", "/openapi.json"),
    docs_url=_get_env("DOCS_URL", "/docs"),
    redoc_url=_get_env("REDOC_URL", "/redoc"),
    redoc_js_url=_get_env(
        "REDOC_JS_URL",
        "https://cdn.jsdelivr.net/npm/redoc@2/bundles/redoc.standalone.js",
    ),
    database_url=_get_env("DATABASE_URL", "sqlite:///./book_api.db"),
    secret_key=_get_env("SECRET_KEY", "development-secret-key"),
    algorithm=_get_env("ALGORITHM", "HS256"),
    access_token_expire_minutes=int(_get_env("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
)

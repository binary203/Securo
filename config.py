import os
import warnings
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.abspath(os.path.dirname(__file__)), "app", ".env"))

app_dir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "fallback-dev-key-change-in-production")
    SEMGREP_API_TOKEN: str = os.environ.get("SEMGREP_APP_TOKEN", "")
    GEMINI_API: str = os.environ.get("GEMINI_API_KEY", "")

    MAX_CONTENT_LENGTH: int = 110 * 1024 * 1024
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"
    REMEMBER_COOKIE_HTTPONLY: bool = True
    REMEMBER_COOKIE_SAMESITE: str = "Lax"
    WTF_CSRF_TIME_LIMIT: int = 3600


class DevelopmentConfig(BaseConfig):
    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///default.db"


class ProductionConfig(BaseConfig):
    DEBUG: bool = False

    _env_secret = os.environ.get("SECRET_KEY")
    if not _env_secret:
        warnings.warn(
            "SECRET_KEY не задан в окружении. Используется небезопасный fallback.",
            stacklevel=2,
        )
    SECRET_KEY: str = _env_secret or BaseConfig.SECRET_KEY

    if not os.environ.get("DATABASE_URL"):
        warnings.warn(
            "DATABASE_URL не задан. Используется SQLite.",
            stacklevel=2,
        )
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL", "sqlite:///production.db"
    )

    SESSION_COOKIE_SECURE: bool = True
    REMEMBER_COOKIE_SECURE: bool = True
    PREFERRED_URL_SCHEME: str = "https"
